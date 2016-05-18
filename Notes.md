# lemur
Bio data collector
# Development Notes
##Part0 Directory Structure
```
~/lemur
        |__ /myapp
                |-- views.py
                |-- models.py
                |-- manage.py
                |-- main.py
                |__ /templates
                        |-- layout.html
                |__ /static
                        |__ /js
                                |--boostrap-select.js
                                |--boostrap.js
                                |--bootstrap.min.js
                                |--jquery-2.1.3.js
                                |--npm.js
                        |__ /fonts
                        |__ /css
                                |--bootstrap-select.css   
                                |--bootstrap-select.css.map
                                |--bootstrap-select.js.map
                                |--bootstrap-theme.css
                                |--bootstrap-theme.css.map
                                |--bootstrap-theme.min.css
                                |--bootstrap.css
                                |--bootstrap.css.map
                                |--bootstrap.min.css                     
        |-- Requirements.txt
        |__ /env
        |--.gitignore
        |--LICENSE
        |--README.md
        |--Notes.md

```

##Part1 Setup
###Step1 Create Virtual Environment for All Required Dependencies
Pip is a Python package manager – a tool for installing Python packages from the Python Package Index<br\>
* Install pip and python3
* Install virtualenvwrapper<br\>
``` pip install virtualenvwrapper ```
For more tutorials about virtualenv(wrapper), please look up at https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_03_beginning_development.markdown
* Create a virtual environment for your app. I’ll name mine todoapp.<br\>
``` mkvirtualenv lemur --python=python3```
* In order to use the created virtual environment type:<br\>
``` workon todoapp ```


###Step2 Install Required Packages: Flask, psycopg2, SQLAlchemy
* install Flask <br\>
```
pip install Flask
```
* To integrate our app with PostgreSQL we need to install:
	* Psycopg2 – a Python adapter for Postgres
	* Flask-SQLAlchemy – Flask wrapper for SQLAlchemy (a powerful relational database framework that offers a high level ORM and low level access to a database’s native SQL functionality for Python.)
	```
	pip install psycopg2 Flask-SQLAlchemy
	```
###Step 3: Create requirements.txt File With All Dependencies Listed
Our application must have a requirements.txt that contains all the package dependencies with the exact versions.
```pip freeze > requirements.txt```
###Step 4: Install PostgreSQL 9.3 and Create Local Database
We’ll need to get a Postgres database set up to store our todo list. We’ll also add Python ORM SQLAlchemy to our app. Once you have Postgres installed, create a database and name it todoapp to use as a local database.<br\>
* Run PostgreSQL command line client.
```psql```
For errors like ```psql: FATAL:  database "<user>" does not exist``` <br\>
Please refer http://stackoverflow.com/questions/17633422/psql-fatal-database-user-does-not-exist
* Create a database user with a password.
``` create user zzy with password 'mypassword'; ```
* Create a database instance.
``` create database Flask_demo owner zzy encoding 'utf-8'; ```
###Step 5: Organize the Structure of the Application

The structure for our web app will be as follows:
```
The todoapp.py file is the Python code that will import the app and execute.
The views.py file contains a view function.
The models.py file contains SQLAlchemy models.
The static folder contains all the css and javascript files.
The templates folder contains Jinja2 templates.
```
For our needs, the structure is simplistic. If you want to know how to structure a large Flask application, take a look at this tutorial: http://gouthamanbalaraman.com/blog/flask-app-directory-structure.html

###Step 6: Setup boostrap
Bootstrap is the most popular front-end framework for web development.<br/>
*You can add Bootstrap to your project by downloading a zip file from the project’s website
*Unzip the compressed file and move the files to the /static folder in the todoapp directory.

###Step 7: Setup boostrap-select
Bootstrap-select is a jQuery plugin that utilizes Bootstrap's dropdown.js to style and bring additional functionality to standard select elements. A form to pick a category and a priority for todo is a simple select list with customized .selectpicker class.
*Download Bootstrap-select
*Unpack the compressed file and move the files to the /static folder in the project directory
*Enable Bootstrap-Select via JavaScript in layout.html.
```('.selectpicker').selectpicker();```


##Part2 Acknowledgement
http://www.vertabelo.com/blog/technical-articles/web-app-development-with-flask-sqlalchemy-bootstrap-part-1#step4

