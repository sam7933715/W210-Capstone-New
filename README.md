# Trip Planner Developer Docs

Virtual Environment Notes:
[Poetry](https://python-poetry.org/docs/basic-usage/) is used to manage dependencies. The expectation is that people will create a Python virtual environment with pyenv and then run some poetry commands to install packages into the virtual environment. For instance, if things are set up correctly, developers can run ```pyenv exec poetry shell``` and then ```poetry install``` in their terminal and all project dependencies will be installed. 

Bayard Venv Steps Taken for Install:
1. Install the correct python version in pyenv. 
```bash
pyenv install 3.9.13
```

2. Create Python virtual Environment
```bash
pyenv virtualenv 3.9.13 model_planner
```
Note: The venv is named model_planner. Your terminal will return a path where the folder is. Save this path. 
Mine is in: `/Users/charlescarlson/.pyenv/versions/3.9.13/envs/model_planner`

If you don't have the path save or are confused. Run: 
```
pyenv versions
```

This will return the versions of python you have installed and return the path of your active pyenv.

3. Activite the correct python env:
I ran:
```
source /Users/charlescarlson/.pyenv/versions/3.9.13/envs/model_planner/bin/activate
```

You need the path to your own pyenv. 
source is a linux/mac command. I think that in Windows you need to adjust your path variables. 
This step specifically just to set the python version in terminal, which any OS can do. 

4. Poetry automatically uses the local pyenv.
```
poetry install
```

Gets all current dependecies.

5. If that's not working, or if you just want to use the venv more generally, start a shell from it with one of the following commands. 

```
pyenv exec <command>
```

often the command is <poetry shell>

```
poetry shell
```