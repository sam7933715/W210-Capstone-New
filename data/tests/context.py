import sys
import os

def add_packages():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
