# lemur
Bio data collector
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
                        |-- form.html
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
``` mkvirtualenv lemur --python=python3```
###Step2 Install Required Packages: Flask, psycopg2, SQLAlchemy
```
pip install -r requirement
```
###Step3: Create Local Database
We’ll need to get a Postgres database set up to store our todo list. We’ll also add Python ORM SQLAlchemy to our app. Once you have Postgres installed, create a database and name it lemur to use as a local database.<br\>
* Run PostgreSQL command line client.<br\>
* Create a database user with a password.<br\>
* Create a database instance.<br\>

```
psql
create user zzy with password 'mypassword';
create database lemur owner zzy encoding 'utf-8'; 
```

###Step4 Run the app
```
cd myapp
python3 main.py
```
For details of setting things up in the first place, please read Notes.md.<br/>
##Part2 Acknowledgement
We borrowed code and templates from the following sources as our start point.<br/>
https://github.com/Gastove/http-demo
http://www.vertabelo.com/blog/technical-articles/web-app-development-with-flask-sqlalchemy-bootstrap-part-1#step4
