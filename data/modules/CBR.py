import gensim
import nltk
import pandas as pd

from collections import Counter
from gensim import corpora
from gensim.summarization import keywords
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rake_nltk import Rake
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from textblob import TextBlob


def sentiment_analysis(df):
    """
    Calculates the sentiment polarity and subjectivity for each business in a dataframe of reviews using the TextBlob package, and returns the results as a new dataframe.

    Parameters:
        - df (pandas.DataFrame): A dataframe containing a 'text' column of textual data.

    Returns:
        - pandas.DataFrame: A copy of the input dataframe with two new columns:
            - 'sentiment_polarity': The average polarity score for each business
            - 'sentiment_subjectivity': The average subjectivity score for each business

    Example:
    >>> df_with_sentiment = sentiment_analysis(df)
    """
    # Create an empty dataframe to hold the sentiment scores
    sentiment_df = pd.DataFrame(
        columns=["business_id", "name", "sentiment_polarity", "sentiment_subjectivity"]
    )

    # Loop through each unique business in the dataframe
    for business_id, group in df.groupby(["business_id", "name"]):
        # Combine all the reviews for this business into a single string
        text = " ".join(group["text"])

        # Calculate the sentiment polarity and subjectivity using TextBlob
        blob = TextBlob(text)
        sentiment_polarity = blob.sentiment.polarity
        sentiment_subjectivity = blob.sentiment.subjectivity

        # Append the sentiment scores to the sentiment dataframe
        sentiment_df = sentiment_df.append(
            {
                "business_id": business_id[0],
                "name": business_id[1],
                "sentiment_polarity": sentiment_polarity,
                "sentiment_subjectivity": sentiment_subjectivity,
            },
            ignore_index=True,
        )

    # Group the sentiment dataframe by business_id / business_name and calculate the average sentiment scores
    sentiment_df = sentiment_df.groupby(["business_id", "name"]).mean().reset_index()

    # Merge the sentiment dataframe back into the original dataframe
    df = pd.merge(df, sentiment_df, on=["business_id", "name"])

    return df


def lda_model(df, num_topics=10, remove_stopwords=True):
    """
    Trains a Latent Dirichlet Allocation (LDA) model on the input dataframe's 'text' column.

    Parameters:
       - df (pandas.DataFrame): A dataframe containing a 'text' column of textual data.
       - num_topics (int): The number of topics to generate from the data. Default is 10.
       - remove_stopwords (bool): Whether or not to remove English stopwords from the text data. Default is True.

    Returns:
       - lda_model (gensim.models.ldamodel.LdaModel): The trained LDA model.
       - dictionary (gensim.corpora.dictionary.Dictionary): The dictionary of terms learned from the text data.

    Example:
    >>> tst_lda, tst_dict = lda_model(tst, num_topics = 10, remove_stopwords = True)
    """
    # Check if omw-1.4 corpus is downloaded
    nltk.download("omw-1.4")

    # Create a list of lists, where each inner list contains the tokens from a review
    tokenized_reviews = [review.split() for review in df["text"]]

    # Remove English stopwords from the tokenized reviews, if specified
    if remove_stopwords:
        english_stopwords = set(stopwords.words("english"))
        tokenized_reviews = [
            [word for word in tokens if word.lower() not in english_stopwords]
            for tokens in tokenized_reviews
        ]

    # Create a dictionary from the tokenized reviews
    dictionary = corpora.Dictionary(tokenized_reviews)

    # Create a document-term matrix from the tokenized reviews and the dictionary
    corpus = [dictionary.doc2bow(tokens) for tokens in tokenized_reviews]

    # Train the LDA model on the corpus
    lda_model = gensim.models.ldamodel.LdaModel(
        corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=10
    )
    return lda_model, dictionary


def extract_topics(df, lda_model, dictionary, num_words=10, remove_stopwords=True):
    """
    Extracts the top topics and words for each review in the input dataframe using a pre-trained LDA model and dictionary.

    Parameters:
        - df (pandas.DataFrame): A dataframe containing a 'text' column of textual data.
        - lda_model (gensim.models.ldamodel.LdaModel): The pre-trained LDA model.
        - dictionary (gensim.corpora.dictionary.Dictionary): The dictionary of terms learned from the text data.
        - num_words (int): The number of top words to include for each topic. Default is 10.
        - remove_stopwords (bool): Whether or not to remove English stopwords from the text data. Default is True.

    Returns:
        - df (pandas.DataFrame): A copy of the input dataframe with additional 'topic_id' and 'topic_words' columns.

    Example:
    >>> df_with_topics = extract_topics(tst, tst_lda, tst_dict, num_words=10, remove_stopwords = True)
    """

    # Define a helper function to get topic words for each review
    def get_topic_words(review):
        # Get the tokens for this review
        tokens = review.split()

        # Remove English stopwords from the tokens, if specified
        if remove_stopwords:
            english_stopwords = set(stopwords.words("english"))
            tokens = [word for word in tokens if word.lower() not in english_stopwords]

        # Get the document-term matrix for this review
        bow = dictionary.doc2bow(tokens)

        # Get the topic distribution for this review
        topic_dist = lda_model[bow]

        # Get the top topic for this review
        top_topic = max(topic_dist, key=lambda x: x[1])

        # Get the top words for the top topic
        top_words = [
            word for word, _ in lda_model.show_topic(top_topic[0], topn=num_words)
        ]

        # Return the topic ID and top words
        return pd.Series({"topic_id": top_topic[0], "topic_words": top_words})

    # Apply the helper function to each row of the dataframe and assign the results to new columns
    df[["topic_id", "topic_words"]] = df["text"].apply(get_topic_words)

    return df


def extract_keywords(df, num_words=10, split_long=True, remove_stopwords=False):
    """
    Extracts keywords from reviews in the 'text' column of a dataframe using the gensim package.

    Parameters:
        - df (pandas.DataFrame): A dataframe containing a 'text' column of textual data.
        - num_words (int): The maximum number of keywords to extract per review (default: 10).
        - split_long (bool): Whether or not to split long reviews into smaller chunks before extracting keywords (default: True).
        - remove_stopwords (bool): Whether or not to remove English stopwords from the reviews before extracting keywords (default: False).

    Returns:
        pandas.DataFrame: A copy of the input dataframe with a new column: 'keywords', which contains a list of the top keywords extracted from each review.

    Example:
    >>> df_with_keywords = extract_keywords(df, num_words=20, remove_stopwords=True)
    """

    # nltk pakcage
    nltk.download("punkt")

    # Define the set of English stopwords if remove_stopwords is True
    if remove_stopwords:
        english_stopwords = set(stopwords.words("english"))
    else:
        english_stopwords = set()

    def extract_keywords_from_review(review):
        # Remove any unwanted characters
        review = review.replace("\n", " ").replace("\r", "")

        # Split long reviews into smaller chunks
        if split_long:
            chunks = review.split(". ")
            keywords_list = []
            for chunk in chunks:
                # Tokenize the chunk and remove English stopwords if specified
                chunk_tokens = [
                    token
                    for token in word_tokenize(chunk)
                    if token.lower() not in english_stopwords
                ]
                # Check if chunk_tokens is empty and skip this chunk if it is
                if not chunk_tokens:
                    continue
                # Extract keywords from the chunk
                r = Rake()
                r.extract_keywords_from_text(" ".join(chunk_tokens))
                chunk_keywords = r.get_ranked_phrases()[:num_words]
                # Split each keyword phrase into separate words and append to the list
                for keyword in chunk_keywords:
                    keywords_list.extend(keyword.split())
        else:
            # Tokenize the review and remove English stopwords if specified
            review_tokens = [
                token
                for token in word_tokenize(review)
                if token.lower() not in english_stopwords
            ]
            # Extract keywords from the entire review
            r = Rake()
            r.extract_keywords_from_text(" ".join(review_tokens))
            keywords_list = r.get_ranked_phrases()[:num_words]
            # Split each keyword phrase into separate words and append to the list
            new_keywords_list = []
            for keyword in keywords_list:
                new_keywords_list.extend(keyword.split())
            keywords_list = new_keywords_list

        return keywords_list

    # Create a new column in the dataframe with the keywords for each review
    df_with_keywords = df.copy()
    df_with_keywords["keywords"] = df_with_keywords["text"].apply(
        extract_keywords_from_review
    )

    return df_with_keywords


def content_based_aggregate(df):
    """
    Aggregates a dataframe by business_id, name, city, and state. For each column, the following operations are performed:
        - stars_y (num): average
        - review_count (num): average
        - sentiment_polarity (num): average
        - sentiment_subjectivity (num): average
        - topic_words (list of words): take all the unique words and keep top 20 words in frequency as list
        - keywords (list of words): take all the unique words and keep top 20 words in frequency as list
        - reviews (list of text): concatenate all reviews for each business as a single string

    Returns:
    pandas.DataFrame: A new dataframe with the following columns:
                      - business_id (str)
                      - name (str)
                      - city (str)
                      - state (str)
                      - stars (float)
                      - review_count (float)
                      - sentiment_polarity (float)
                      - sentiment_subjectivity (float)
                      - topic_words_top20 (list of str)
                      - keywords_top20 (list of str)
                      - reviews (str)
    """
    # Aggregate by business_id, name, city, and state
    agg_df = df.groupby(["business_id", "name", "city", "state"]).agg(
        {
            "stars_y": "mean",
            "review_count": "mean",
            "sentiment_polarity": "mean",
            "sentiment_subjectivity": "mean",
            "topic_words": lambda x: [
                word
                for word, count in Counter(
                    [item for sublist in x for item in sublist]
                ).most_common(20)
            ],
            "keywords": lambda x: [
                word
                for word, count in Counter(
                    [item for sublist in x for item in sublist]
                ).most_common(20)
            ],
            "text": lambda x: " ".join(x),
        }
    )

    # Rename columns
    agg_df = agg_df.rename(
        columns={
            "stars_y": "stars",
            "review_count": "review_count",
            "sentiment_polarity": "sentiment_polarity",
            "sentiment_subjectivity": "sentiment_subjectivity",
            "topic_words": "topic_words_top20",
            "keywords": "keywords_top20",
            "text": "reviews",
        }
    )

    return agg_df.reset_index()


def calc_cosine_similarity(df, business_name, my_city, destination_city):
    """
    Calculate cosine similarity between the target business in my_city and businesses in destination_city
    based on five features: sentiment polarity, sentiment subjectivity, top 20 topic words, top 20 keywords,
    and reviews.

    Parameters:
        - df (pandas.DataFrame): The aggregated dataframe containing the business data.
        - business_name (str): The name of the target business in my_city.
        - my_city (str): The city where the target business is located.
        - destination_city (str): The city where the destination businesses are located.

    Returns:
    pandas.DataFrame: A dataframe containing the cosine similarity scores for each feature and the integer rank
    for each feature, sorted by ascending rank.
    """

    # Filter the dataframe to get the target business in my_city
    target_business = df[(df["name"] == business_name) & (df["city"] == my_city)]

    # If there are multiple businesses with the same name, choose the one with highest star rating and most review count
    if len(target_business) > 1:
        target_business = target_business.sort_values(
            by=["stars", "review_count"], ascending=[False, False]
        )
        target_business = target_business.iloc[0]
    target_business = target_business.reset_index(drop=True)

    # Filter the dataframe to get businesses in destination_city
    destination_businesses = df[df["city"] == destination_city]

    # Compute cosine similarity for each column
    cosine_similarities = {}
    for col in [
        "sentiment_polarity",
        "sentiment_subjectivity",
        "topic_words_top20",
        "keywords_top20",
        "reviews",
    ]:
        if col == "reviews":
            # Concatenate all reviews for each business into one string
            target_reviews = " ".join(target_business[col])
            destination_reviews = destination_businesses[col].apply(
                lambda x: " ".join(x)
            )
            # Compute cosine similarity using TfidfVectorizer to convert text into vectors
            vectorizer = TfidfVectorizer(
                max_features=1000, min_df=1, use_idf=True
            ).fit_transform([target_reviews] + list(destination_reviews))
            cosine_similarities[col] = cosine_similarity(vectorizer)[1:, 0].tolist()

        elif col in ["topic_words_top20", "keywords_top20"]:
            # Combine the target and destination businesses' lists of words and count their frequency
            target_words = " ".join(target_business[col][0])
            destination_words = (
                destination_businesses[col].apply(lambda x: " ".join(x)).tolist()
            )
            all_words = [target_words] + destination_words
            vectorizer = CountVectorizer().fit_transform(all_words)
            vectorizer_dense = vectorizer.toarray()
            cosine_similarities[col] = cosine_similarity(
                vectorizer_dense[0:1], vectorizer_dense[1:]
            ).tolist()[0]
        else:
            # Compute cosine similarity using the numerical column values
            print(target_business[col])
            print(destination_businesses[col])
            cosine_similarities[col] = cosine_similarity(
                target_business[[col]], destination_businesses[[col]]
            ).tolist()[0]

    # Create a dataframe with the cosine similarity scores for each column
    similarity_df = pd.DataFrame(cosine_similarities)
    similarity_df["business_id"] = destination_businesses["business_id"].reset_index(
        drop=True
    )
    similarity_df["name"] = destination_businesses["name"].reset_index(drop=True)
    similarity_df["city"] = destination_businesses["city"].reset_index(drop=True)
    similarity_df["state"] = destination_businesses["state"].reset_index(drop=True)
    similarity_df = similarity_df[
        [
            "business_id",
            "name",
            "city",
            "state",
            "sentiment_polarity",
            "sentiment_subjectivity",
            "topic_words_top20",
            "keywords_top20",
            "reviews",
        ]
    ]

    # Calculate integer rank for each column
    similarity_df_rank = (
        similarity_df[
            [
                "sentiment_polarity",
                "sentiment_subjectivity",
                "topic_words_top20",
                "keywords_top20",
                "reviews",
            ]
        ]
        .rank(ascending=False, method="dense")
        .astype(int)
    )
    similarity_df_rank.columns = [
        "sentiment_polarity_rank",
        "sentiment_subjectivity_rank",
        "topic_words_top20_rank",
        "keywords_top20_rank",
        "reviews_rank",
    ]
    similarity_df = pd.concat([similarity_df, similarity_df_rank], axis=1)

    # Sort by ascending rank
    similarity_df = similarity_df.sort_values(
        by=[
            "sentiment_polarity",
            "sentiment_subjectivity",
            "topic_words_top20",
            "keywords_top20",
            "reviews",
        ]
    )

    return similarity_df


def content_based_recommender(df):
    """
    Generate a content-based recommendation list based on the average rank of the five features: sentiment polarity,
    sentiment subjectivity, top 20 topic words, top 20 keywords, and reviews.

    Parameters:
        - df (pandas.DataFrame): The dataframe containing the cosine similarity scores and ranks for each business.

    Returns:
        - pandas.DataFrame: A dataframe containing the top 10 recommended businesses based on the average rank of the
    five features.
    """
    df["avg_rank"] = df[
        [
            "sentiment_polarity_rank",
            "sentiment_subjectivity_rank",
            "topic_words_top20_rank",
            "keywords_top20_rank",
            "reviews_rank",
        ]
    ].mean(axis=1)
    return df.sort_values(by="avg_rank", ascending=True).reset_index(drop=True)[:10]
