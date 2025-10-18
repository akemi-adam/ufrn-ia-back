import environ
import os

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), "../.env")) 

def get_env(var_name, default=None):
    return env(var_name, default=default)
