import pickle


def save_model(filename, modelObject):
    """ filename : string containing target filename
        modelObject : model object """
    f = filename
    ml = modelObject

    with open(f, 'wb') as f:
        pickle.dump(ml, f)


def load_model(filename):
    """ pass in a file name. Output will be pickle file containing model
        You can then predict as usual"""
    with open(filename, 'rb') as f:
        ml = pickle.load(f)

    return ml
    
