<div align="center">
  <img src="https://github.com/SenteraLLC/py-sentera-api/blob/feature-documentation/images/senteralogo.png">
</div>

# Getting Started
* <a href="#introduction">Introduction</a>
* <a href="#py-sentera-api">py-sentera-api</a>
* <a href="#installation">Installation</a>
* <a href="#examples">Examples</a>
* <a href="#documentation">Documentation</a>

<a href="#introduction"></a>
## Introduction

Sentera provides multiple APIs (Application Programming Interfaces) to be used together to power its platforms and libraries for sensors. Use the API to connect global networks around the world to allow researchers and developers to configure sensors for planning and flight for agricultural research, weather data, drone images, satellite images, maps, elevations, soil datasets, measuring, integration, and other uses. The py-sentera-api can be used to integrate data into your application.

If you have questions regarding this API, datasets, or other documentation, contact support@sentera.com.

<a href="#py-sentera-api"></a>
## py-sentera-api

Python library to access Sentera data through GraphQL API.

<a href="#installation"></a>
### Installation

If using within your own python environment/script, install with:

    pip install git+https://github.com/SenteraLLC/py-sentera-api.git

Else to get started with examples right away, simply follow the *Examples* instructions.

<a href="#examples"></a>
### Examples

1. Follow this [link](https://colab.research.google.com/drive/1XMoviBHAyd9-rMYorq9JO1mjs64U9WEn) to a Google CoLab example notebook.
2. Click the button *Open in Playground* in the top left.
3. Click the button *Connect* in the top right.
4. Code examples can be run by clicking the play buttons next to them.  Make sure to run the
   setup code first.  You'll have to enter your Sentera username and password.
5. If you want to save your changes, click *Copy to Drive* in the top left.

<a href="#documentation"></a>
### Documentation

This library is documented using Sphinx. To generate documentation, make sure all **dev**
dependencies are installed (e.g. you've installed via ``pip install -e .[dev]``).  Within
the *docs/* subdirectory, run:

    make html

The documentation will be generated as an html file located at *py-sentera-api/docs/\_build/html/index.html*.
Open with a browser to get more in depth information on the various modules and functions within the library.
