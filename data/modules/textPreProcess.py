"""A module to complete basic text preprocess steps.

A set of functions are provided that can help with text prepocessing.
Either:
    (1) Use the map_func in a map step to fix all of the text. 
    (2) Get a sklearn vectorizer that has been fit already with preprocessed text. 
"""

import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer


def map_func(text):
    """ Is designed to be mapped over a DF column with text for the ML algorithm. 
    
    Args:
        text - str: A string to convert to preprocessed text for review. 
    """

    # Set Lower:
    text = text.lower()

    # Remove Numbers
    text = re.sub(r'\d+', '', text)

    # Remove Punctuation
    text = text.translate(text.maketrans("",""), text.punctuation)

    # Remove Whitespace
    text = text.strip()

    return text

def get_tokenizer(df, train_col):
    """Add a Pandas Dataframe that 
    
    Args:
        df - pandas.DataFrame: A dataframe with columns to train a tokenizer on. 
        train_col - str: A column name to train the vectorizer on. 
    """

    data = df[train_col].map(map_func)
    
    vectorizer = TfidfVectorizer(stop_words="english")

    return vectorizer.fit_transform(data)
