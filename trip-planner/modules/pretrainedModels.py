"""This module holds a class to import models and add methods that the app needs"""

import pickle


def save_model(filename, modelObject):
    """
    Saves model output to a pickle file for later use.
    Parameters:
        - filename: pathname string for target filename
        - modelObject: model object
    Returns:
        - N/A 
    """
    f = filename
    ml = modelObject

    with open(f, 'wb') as f:
        pickle.dump(ml, f)


def load_model(filename):
    """ 
    Loads model from saved pickle file. Just need to pass filename path of pre-saved model
    Parameters:
        - filename: pathname string of saved pickle file containing pre-trained model
    Returns:
        - model object from saved pickle file
     """
    with open(filename, 'rb') as f:
        ml = pickle.load(f)

    return ml
    
