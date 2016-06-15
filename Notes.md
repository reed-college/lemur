# lemur
Bio data collector
# Development Notes

##Part0 Directory Structure
```
~/lemur
        |__ /myapp
                |-- __main__.py
                |-- main.py
                |-- config.py
                |-- db.py
                |-- schema.py
                |__ /templates
                        |--layout.html
                        |--common_home.html
                        |--admin_home.html
                        |--admin_log_out.html
                        |--admin_manage_users.html
                        |--admin_modify_lab.html
                        |--admin_retrieve_data.html
                        |--admin_setup_classes.html
                        |--admin_setup_labs.html
                        |--admin_setup_labs_and_data_access.html
                        |--student_data_entry.html
                        |--student_enter_data.html
                        |--student_home.html       
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
        |--requirements.txt
        |--settings.cfg 
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
``` workon lemur ```


###Step2 Install Required Packages: Flask, psycopg2, SQLAlchemy, WTForms, Flask-WTF
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
* install WTForms, Flask-WTF and Flask-Script```pip install WTForms Flask-WTF```


###Step 3: Create requirements.txt File With All Dependencies Listed
Our application must have a requirements.txt that contains all the package dependencies with the exact versions.
```pip freeze > requirements.txt```

###Step 4: Install PostgreSQL 9.3 and Create Local Database
We’ll need to get a Postgres database set up to store our todo list. We’ll also add Python ORM SQLAlchemy to our app. Once you have Postgres installed, create a database and name it lemur to use as a local database.<br\>
* Run PostgreSQL command line client.<br\>
* Create a database user with a password.<br\>
* Create a database instance.<br\>

```
psql
create user zzy with password 'mypassword';
create database lemur owner zzy encoding 'utf-8'; 
```


For errors like ```psql: FATAL:  database "<user>" does not exist``` <br\>
Please refer http://stackoverflow.com/questions/17633422/psql-fatal-database-user-does-not-exist

###Step 5: Organize the Structure of the Application

The structure for our web app will be as follows:
```
The main.py file is the Python code that will import the app and execute.
The schema.py file contains SQLAlchemy models.
The config.py file contains the setup of the application
The dataforms.py file contains all the WTForms.
The db.py file contains the setup of the database.
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
`('.selectpicker').selectpicker();`

###Step8: Download and Link boostrap library, jquery-ui 1.11.4 library, and jquery-2.1.3 library


###Step9: Run the app `python3 myapp`

###Step10: Set up tables in the database by entering `http://127.0.0.1:5000/admin/bootstrap` in the address line and click `Return`

##Part2 Development process
1.Preparation
* Play around with the existing bio data-collector at: <http://collector.reed.edu/>
* Draw a flowchart to represent the connections between webpages at: <http://i.imgur.com/kgKyxrH.png>
* Design the file structure. We mimic the style at: <http://gouthamanbalaraman.com/blog/flask-app-directory-structure.html>

2.Get started
* We begin to write Python for schema.py and HTML/CSS(using CSS boostrap) code for the design of the main page.  

##Part3 Study Guide
We work through my demo, which is built on top of Ross's http-demo
###0.To understand Python,CSS,HTML,Javascript(JQuery) files in general, please check out the references in Part4.

###1.To understand code in: `settings.cfg config.py db.py`
* Read the first part of the documentation of configuration in python3 at: <https://docs.python.org/3/library/configparser.html>
* Read the first part of the documentation of sessionmaker at: <http://docs.sqlalchemy.org/en/latest/orm/session_api.html#session-and-sessionmaker>

###2.To understand code in: `main.py schema.py`
* Read a quick start tutorial for Flask at: <http://flask.pocoo.org/docs/0.10/quickstart/#a-minimal-application>
* Read a tutorial for Flask-Alchemy at: <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html>
* Skim through the documentation of enum at: <https://docs.python.org/3/library/enum.html>

###3.To understand code in: `dataforms.py`
* Read a short tutorial of WTForms at <http://wtforms.readthedocs.io/en/latest/crash_course.html> <br>
* Read WTForms in Flask at: <http://flask.pocoo.org/docs/0.10/patterns/wtforms/>

###4.To understand code in: `create_lab.html`
* One specific use of JQuery at <https://www.codecademy.com/courses/web-beginner-en-v6phg/2/3?curriculum_id=50a3fad8c7a770b5fd0007a1>


##Part4 References
###1.Tools
####1.general development environment
* A good intro at: <https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_01_development_environment.markdown>

* virtualenv/virtualenvwrapper and some basic terminal commands at https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_03_beginning_development.markdown

####2.github
* A quick-start at: <https://guides.github.com/activities/hello-world/>
* A useful cheat-sheet at: <https://education.github.com/git-cheat-sheet-education.pdf>
* A relatively complete intro to git/github at: <https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_02_git.markdown>

####3.ssh
* Notes at: <https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_04_ssh_plain_text.markdown>

####4.network
* Basic concepts of http/html at: <https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_05_http_and_html.markdown> 

####5.database/ORM
* Basic concepts of database(Postgresql) and ORM at: <br>
<https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_06_databases_part_one.markdown>
<https://github.com/reed-college/2016_sds_lesson_notes/blob/master/lesson_06_databases_part_two.markdown>


###2.Language related
####1.Python3
* A general survey/review of the basics of Python3 at <http://www.tutorialspoint.com/python3/> 
* A good short interactive lesson of Python at: <https://www.codecademy.com/courses/introduction-to-python-6WeG3/0/1?curriculum_id=4f89dab3d788890003000096>

####2.HTML/CSS
* A quick start of HTML at: <https://www.codecademy.com/en/courses/make-a-website/lessons/site-structure/exercises/html-css?action=resume>
* A useful glossary of HTML at: <https://www.codecademy.com/articles/glossary-html>
* Basic concept of CSS at: <https://developer.mozilla.org/en-US/docs/Web/CSS/Syntax>
* Make a HTML table at: <http://www.tablesgenerator.com/html_tables>
* A good short interactive lesson of HTML/CSS at: <https://www.codecademy.com/courses/web-beginner-en-HZA3b/0/1?curriculum_id=50579fb998b470000202dc8b>
* A survey of CSS selector at: <https://css-tricks.com/how-css-selectors-work/>
* A useful guide to CSS flexbox at: <https://css-tricks.com/snippets/css/a-guide-to-flexbox/>
* My personal favorite reference for HTML at: <https://developer.mozilla.org/en-US/docs/Web/CSS/Reference> and for CSS at: <https://developer.mozilla.org/en-US/docs/Web/Guide/HTML>


####4.Javascript
* A good short interactive lesson of JQuery(jQuery is a library, or set of helpful add-ons, to the JavaScript) at: <https://www.codecademy.com/courses/web-beginner-en-bay3D/0/1?curriculum_id=50a3fad8c7a770b5fd0007a1> 
* Intro to JSON(first half should be enough) at: <https://msdn.microsoft.com/en-us/library/bb299886.aspx>
* JQuery doc at: <http://jquery.com/>
* Introduction of Javascript(go through from "Intro" to "Expressions and operators") at: <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Introduction>
* A good short interactive lesson of Javascript at: <https://www.codecademy.com/courses/getting-started-v2/0/1?curriculum_id=506324b3a7dffd00020bf661>
* An explanation with examples of Javascript object at: <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Working_with_Objects>
* An explanation with examples of Javascript array at: <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array>

####5.Boostrap
* We use boostrap to make our life easier.<br> 
A general survey of boostrap CSS at: <http://getbootstrap.com/css/> 
A general survey of boostrap JavaScript at: <http://getbootstrap.com/javascript/>


####6.Flask
* We use Flask as the architecture. A quick start tutorial at: <http://flask.pocoo.org/docs/0.10/quickstart/#a-minimal-application>

* Jinja2 HTML template(default template engine of Flask) at <http://jinja.pocoo.org/docs/dev/templates/>

* We use WTForm library to handle form data submitted by a browser. Flask-WTF offers simple integration with WTForms <br>
a short tutorial at <http://wtforms.readthedocs.io/en/latest/crash_course.html> <br>
WTForms in Flask at: <http://flask.pocoo.org/docs/0.10/patterns/wtforms/>
* We use Flask-Alchemy as our ORM to interact with Postgresql. 
A tutorial for Flask-Alchemy at: <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html> <br>
Flask-Alchemy in Flask at: <http://flask.pocoo.org/docs/0.10/patterns/sqlalchemy/> <br>
Quick start for flask-wtf at: <https://flask-wtf.readthedocs.io/en/latest/quickstart.html>
* Complex validation of user info with Flask-wtf at: <http://flask.pocoo.org/snippets/64/>

* An example of how to communicate between python and JQuery at: <http://flask.pocoo.org/docs/0.10/patterns/jquery/>

####7.Configuration
* Documentation of configuration in python3 at: <https://docs.python.org/3/library/configparser.html>

####8.Network in JQuery and Flask
* A tutorial of how to build/test RESTful Web API built by python&flask at <http://blog.luisrei.com/articles/flaskrest.html>
* JSON encoding on the client side at: <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify>
* Pass data from client to server at: <https://api.jquery.com/jquery.post/>
* JSON encoding and decoding on the server side at: <http://simplejson.readthedocs.io/en/latest/#encoders-and-decoders>

####9.demos
* A good tutorial/demo used to set environment up and combine all the things above at: <http://www.vertabelo.com/blog/technical-articles/web-app-development-with-flask-sqlalchemy-bootstrap-part-1#step4>
* Another good demo at: <https://github.com/Gastove/http-demo>



