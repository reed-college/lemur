# lemur
Bio data collector
##Part-1 TBD
1.Connect the current webpages with reed login webpage and add power to different accounts/Design a manage user page<br>
2.Better UI design<br>
3.Test the program<br> 
4.Finish writeup and wrap up the app<br>

##Part0 Directory Structure
```
~/lemur
        |__ /myapp
                |-- __main__.py
                |-- main.py
                |-- config.py
                |-- db.py
                |-- schema.py
                |-- utility.py
                |__ /templates
                        |--layout.html
                        |--common_home.html
                        |--admin_edit_data.html                    
                        |--admin_setup_labs_and_data_access.html
                        |--admin_home.html                                       
                        |--admin_log_out.html                                     
                        |--admin_manage_users.html                 
                        |--admin_modify_lab.html                   
                        |--admin_select_lab_for_data.html          
                        |--admin_setup_labs.html  
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
                                |--sortable.js
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
``` mkvirtualenv lemur --python=python3```

###Step2 Install Required Packages: Flask, psycopg2, SQLAlchemy, WTForms, Flask-WTF
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

###Step4: Download and Link boostrap library, jquery-ui 1.11.4 library, and jquery-2.1.3 library

###Step5: Run the app `python3 myapp`

###Step6: Set up tables in the database by entering `http://127.0.0.1:5000/admin/bootstrap` in the address line and click `Return`

For details of setting things up in the first place, please read Notes.md.<br/>

##Part2 Acknowledgement
We borrowed some code and templates from the following sources as our start point.<br/>
https://github.com/Gastove/http-demo
http://www.vertabelo.com/blog/technical-articles/web-app-development-with-flask-sqlalchemy-bootstrap-part-1#step4
