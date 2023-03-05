"""This module holds a class to import models and add methods that the app needs"""

import random as rand

class pretrainedModel():
    """Takes in a pretrained model and adds methods for use by the app."""

    def __init__(self, model):
        self.model = model
    
    def similarity(self, X, Y):
        """A helper function to list how similar two establishments are."""

        # This doesn't currently have useful functionality. 
        # This needs to be updated to determine how similar two points are using cosine similarity. 
        return rand.random()