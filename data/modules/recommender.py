import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

# Content-based Recommender
def recommend_restaurants(input_restaurant_name, my_city, dest_city, businesses,
                          reviews, vectorizer = TfidfVectorizer(stop_words = 'english'), top_n = 10):
    """
        This function recommends similar restaurants in a destination city based on a restaurant name in the user's current city.

        Parameters:
            - input_restaurant_name (str): The name of the restaurant in the user's current city that they would like to
                                           find similar restaurants in the destination city.
            - my_city (str): The city where the input restaurant is located.
            - dest_city (str): The city where the user wants to find similar restaurants.
            - businesses (pandas.DataFrame): A DataFrame that contains information about businesses,
                                             including their name and location.
            - reviews (pandas.DataFrame): A DataFrame that contains information about reviews for businesses,
                                          including the text of the review and the business it was left for.
            - vectorizer (TfidfVectorizer, optional): A TfidfVectorizer object that is used to vectorize the text of the
                                                      reviews. The default is a new instance of the TfidfVectorizer class.
            - top_n (int, optional): number of output to return. Default is 10.

        Returns:
            - pandas.DataFrame or str: Returns a DataFrame with columns 'name', 'business_id', 'categories', 'similarity_score', 'avg_rating', and 'city'
                                       if similar restaurants are found in the destination city.
                Returns a string if:
                - The input restaurant is not found in the source city.
                - No reviews are found for the target business.
                - No similar business is found in the destination city.
    """
    
    # Convert both the input and the names in the 'businesses' data to lowercase
    input_restaurant_name = input_restaurant_name.lower()
    businesses['name'] = businesses['name'].str.lower()
    businesses['city'] = businesses['city'].str.lower()
    
    # Filter the businesses data to only include those in the source city
    businesses_in_my_city = businesses[businesses['city'] == my_city.lower()]
    
    # Find the row in the 'businesses' data where the name matches the input
    target_business = businesses_in_my_city[businesses_in_my_city['name'] == input_restaurant_name]
    
    # Check if there is a matching business name
    if target_business.empty:
        return 'Business not found in source city'
    
    target_business_id = target_business.iloc[0]['business_id']
    
    # Filter reviews data to only include reviews for the target business
    target_reviews = reviews[reviews['business_id'] == target_business_id]
    
    # Check if target_reviews is empty
    if target_reviews.empty:
        return "No reviews found for the target business"
    
    # Concatenate the text of all the reviews for the target business
    text = " ".join(review for review in target_reviews['text'])
    
    # Vectorize the text
    X = vectorizer.fit_transform([text])
    
    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(X, X).flatten()
    
    # Find the indices of the most similar reviews
    related_review_indices = cosine_similarities.argsort()[:-11:-1]
    
    # Get the business_ids of the most similar reviews
    similar_business_ids = [reviews.iloc[index]['business_id'] for index in related_review_indices]
    
    # Filter businesses data to only include the most similar businesses
    similar_businesses = businesses[businesses['business_id'].isin(similar_business_ids)]
    
    # Remove the target business
    similar_businesses = similar_businesses[similar_businesses['business_id'] != target_business_id]
    
    # Filter the 'categories' column to only include categories without 'Restaurants'
    similar_businesses = similar_businesses[~similar_businesses['categories'].str.contains("Restaurants")]
    
    # Filter the businesses data to only include those in the destination city
    similar_businesses_in_dest_city = similar_businesses[similar_businesses['city'] == dest_city.lower()]
    
    # If there is no similiar businesses, return a string saying there is none
    if similar_businesses_in_dest_city.empty:
        return 'No similar business found in destination city'
    
    # Get the cosine similarity scores for the most similar businesses
    similarity_scores = [cosine_similarities[related_review_indices[i]] for i in range(len(related_review_indices))]
    
    # Get the average ratings
    avg_ratings = [reviews[reviews['business_id'] == business_id]['stars'].mean() for business_id in similar_business_ids]
    
    # Create a table with business name, categories, and similarity score
    result = pd.DataFrame({'name': similar_businesses['name'], 
                           'business_id': similar_business['business_id'],
                           'categories': similar_businesses['categories'], 
                           'similarity_score': similarity_scores,
                           'avg_rating': avg_ratings})
    
    # Sort the table by similarity score in descending order
    result = result.sort_values(by=['similarity_score', 'avg_rating'], ascending=[False, False])
    
    return result.head(top_n)

# Item-basd Recommender
def recommend_restaurants_item_based(input_restaurant_name, my_city, dest_city,
                                     businesses, reviews, top_n = 10):
    """
        Given an input restaurant name and two cities, this function recommends similar restaurants in the destination city
        by comparing the categories of businesses. The similarity score and average rating of each restaurant is calculated,
        and the top top_n most similar and highly rated restaurants are returned.

        Parameters:
            - input_restaurant_name (str): The name of the input restaurant.
            - my_city (str): The city of the input restaurant.
            - dest_city (str): The destination city to recommend similar restaurants.
            - businesses (pandas.DataFrame): A DataFrame containing information about businesses,
                                             including business name, ID, city, and categories.
            - reviews (pandas.DataFrame): A DataFrame containing information about reviews, including business ID and rating.
            - top_n (int): The number of restaurants to recommend (default is 10).

        Returns:
            - pandas.DataFrame: A DataFrame containing the name, ID, categories, similarity score, and average rating
                                of the top top_n most similar and highly rated restaurants in the destination city.
    """
    
    # Convert the input restaurant name and the names in the 'businesses' data to lowercase
    input_restaurant_name = input_restaurant_name.lower()
    businesses['name'] = businesses['name'].str.lower()
    
    # Filter the businesses data to only include those in the user's city
    my_city_businesses = businesses[businesses['city'] == my_city]
    
    # Find the row in the 'businesses' data where the name matches the input
    target_business = my_city_businesses[my_city_businesses['name'] == input_restaurant_name]
    
    # Check if there is a matching business name in the user's city
    if target_business.empty:
        return 'Business not found in your city'
    
    target_business_id = target_business.iloc[0]['business_id']
    
    # Filter the businesses data to only include those in the destination city
    dest_city_businesses = businesses[businesses['city'] == dest_city]
    
    # Create an empty list to store the similarity scores for each business
    similarity_scores = []
    
    # Loop through each business in the destination city
    for i, business in dest_city_businesses.iterrows():
        # Get the categories of the target business and the current business
        target_categories = set(target_business['categories'].iloc[0].split(", "))
        current_categories = set(business['categories'].split(", "))
        
        # Calculate the Jaccard similarity between the target business and the current business
        similarity_score = len(target_categories & current_categories) / len(target_categories | current_categories)
        
        # Store the similarity score for the current business
        similarity_scores.append((business['business_id'], similarity_score))
    
    # Sort the list of similarity scores in descending order
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    # Filter the 'businesses' data to only include the most similar businesses
    similar_businesses = businesses[businesses['business_id'].isin([x[0] for x in similarity_scores])]

    # Remove the target business
    similar_businesses = similar_businesses[similar_businesses['business_id'] != target_business_id]

    # If there are no similar businesses in the destination city, return a message saying so
    if similar_businesses.empty:
        return 'No similar businesses found in the destination city'

    # Create a list of business IDs for the most similar businesses in the destination city
    business_ids = similar_businesses['business_id'].tolist()
    
    # Get the average rating for each similar business
    avg_ratings = []
    for business_id in business_ids:
        ratings = reviews[reviews['business_id'] == business_id]['stars'].mean()
        avg_ratings.append((business_id, ratings))

    # Sort the list of average ratings in descending order
    avg_ratings = sorted(avg_ratings, key=lambda x: x[1], reverse=True)

    # Similarity score dictionary
    similarity_scores_dict = {x[0]: x[1] for x in similarity_scores}
    
    # Return the names of the most highly rated restaurants
    recommendations = []
    for business_id, avg_rating in avg_ratings:
        business = similar_businesses[similar_businesses['business_id'] == business_id].iloc[0]
        recommendations.append({'name': business['name'],
                                'business_id': business['business_id'],
                                'categories': [x for x in business['categories'].split(", ") if x != 'Restaurants'],
                                'similarity_score': similarity_scores_dict[business_id],
                                'avg_rating': avg_rating})

    df = pd.DataFrame(recommendations)
    df = df.sort_values(by=['similarity_score', 'avg_rating'], ascending=[False, False])
    df.reset_index(drop = True, inplace = True)
    
    return df.head(top_n)