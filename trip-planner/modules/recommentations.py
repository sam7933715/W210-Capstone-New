"""This module introduces a class to manage making recommendations.

The general workflow is:
  - Initialize with the dataset and a model that's pretrained.
  - Have a function to take in user liked establishments and returns recommendations.
    - Should incorporate whether a user liked or disliked a destination. 
  - Have functions to collect user feedback and store this feedback. 

In the end application, Flask will filter the data for the city preferences, pass this
into recommendationApp along with the pretrained model, and get results to show the
user.
"""

import random as rand
import pandas as pd

class recommenationApp:
    """Application to run a recommendations model on user selected feedback."""

    def __init__(self, model, home_city_estabs, target_city_estabs, returnCount=20):
        """Sets up the recomenationApp
        
        Args:
            model: A machine learning model that recommends establishments to users. 
            home_city_estabs: A Pandas DF with the establishments of the home city. 
                - assume that this is of class pretrainedModel from pretrainedModels.py
            target_city_estabs: An Pandas DF with the establishments of the home city. 
            returnCount: An int with how many establishments to suggest when called. 
        """
        self.model = model
        self.home_city_estabs = home_city_estabs
        self.target_city_estabs = target_city_estabs
        self.returnCount = returnCount

    def homeEstabs(self):
        """Returns establishements in the home city for the user's review."""
        # This currently returns random establishments. A future version should return
        # establishments with a degree of randomness and popularity scores as well. 

        df = self.home_city_estabs
        df["sorter"] = pd.Series(rand.random())
        df = df.sort_values(by=["sorter"], ascending=True)

        return df[:self.returnCount] # returns the top 3 results right now. 

    def updatePreferences(self, preferences):
        """Take in the user preferences based on listed likes/dislikes.
        
        Args:
            preferences: List of tuples with user preferences. (estab, like/disliked).
                - [(str, str)]
        """

        self.preferences = preferences

    def _distanceMap(row, estab_data, model):
        """A helper function to be mapped to a DF to return a pd.series with distances
        between a target and each row.
        
        Uses cosine_similarity. Assumes that the features of row are accessible as a
        column called "features".
        """

        return model.similarity(row["features"], estab_data)

    def targetEstabs(self):
        """Returns recommended establishments based on user preferences."""

        df = self.target_city_estabs
        df["preference"] = 0

        for estab in self.preferences:
            if estab[1] == "like": # The user likes the establishment. 
                df["preferences"] = df["preferences"] + df.map(lambda x: _distanceMap(X, estab, self.model))
            else:
                df["preferences"] = df["preferences"] - df.map(lambda x: _distanceMap(X, estab, self.model))
        
        df = df.sort_values(by = ["preferences"], ascending=False)

        return df[:self.returnCount]
