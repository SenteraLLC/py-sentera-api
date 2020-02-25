## py-sentera-api

Python library to access Sentera data through GraphQL API

### Installation 

If using within your own python environment/script, install with:

    >> pip install git+https://github.com/SenteraLLC/py-sentera-api.git
   
Else to get started with examples right away, simply follow the *Examples* instructions.
        
### Examples

1) Follow this [link](https://colab.research.google.com/drive/1XMoviBHAyd9-rMYorq9JO1mjs64U9WEn) to a Google CoLab example notebook
2) Click the button *Open in Playground* in the top left.
3) Click the button *Connect* in the top right.
4) Code examples can be run by clicking the play buttons next to them.  Make sure to run the 
   setup code first.  You'll have to enter your Sentera username and password.
5) If you want to save your changes, click *Copy to Drive* in the top left.

### Documentation

This library is documented using Sphinx. To generate documentation, within the top level of
the repo, run

    >> sphinx-apidoc -o docs/_modules -M <pkg_name>
    >> cd docs
    >> make html

The documentation will be generated as an html file located at *py-sentera-api/docs/\_build/html/index.html*. 
Open with a browser to get more in depth information on the various modules and functions within the library.
