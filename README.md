## py-sentera-api

Python api to access Sentera data through GraphQL

### Installation 

#### SSH Setup

This library depends on private github repositories, and the setup tools use ssh to access them.  You need to 
link ssh keys on your computer with your github account in order to install this library using the provided
setup tools.  For Windows, make sure you have downloaded the correct [Git Bash](https://gitforwindows.org/) to
run the necessary commands.  For Linux, use a normal terminal.

Git SSH Setup Instructions: https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Test your SSH setup with:

    >> ssh -T git@github.com

#### Windows (Conda)
    
1) Download [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Python3.6

2) Open Anaconda Prompt and clone **py-sentera-api** with

        >> git clone git@github.com:SenteraLLC/py-sentera-api.git

3) Open Anaconda Prompt and navigate to **py-sentera-api**.  Run

        >> start-ssh-agent
        >> conda env create -f environment.yml
        >> conda activate sentera-api
        >> pip install -e .
        
4) This creates an *sentera-api* environment that all scripts should be run in and installs the **sentera**
   library for the scripts to reference.
   
#### Linux (Pipenv)

1) If not installed, install pipenv.

        >> pip install --user pipenv
        
2) Set your PATH to point to the pipenv executable by adding the following to ~/.profile

        export PATH="$PATH:~/.local/bin"

3) Check installation:

        >> source ~/.profile
        >> pipenv -h

4) Open terminal and clone **py-sentera-api** with

        >> git clone git@github.com:SenteraLLC/py-sentera-api.git

5) Navigate to **py-sentera-api** and run

        >> pipenv install
        
6) Run all scripts with:

        >> pipenv run scripts/<script.py> [--args]
   
### Documentation

This library is documented using sphinx. Generate the documentation with the following commands

    >> cd py-sentera-api/doc/
    >> make html

The documentation will be generated as an html file located at *py-sentera-api/doc/\_build/html/index.html*.  
Open with a browser to get more in depth information on the various modules and functions within the library.