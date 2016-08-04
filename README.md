# lemur
Bio data collector
##TBD
* Refactor code
* Better UI design
* Better the current unit testing functions
* Connect the current webpages with reed login webpage and deploy the app on reed server
* Finish writeup/documentation and wrap up the app

##Part1 App General Description
This is a data collector for biology class.<br>
It has three groups of users and corresponder powers.<br> 
###Student: 
* A student can select a lab they belong to and enter one or more group of data according to the required format. 

###Admin:
* An admin can select a lab they belong to and enter one or more group of data according to the required format.
* An admin can create a new lab for their class.
* An admin can view/modify/download data collected for the labs they created.

###SuperAdmin:
* A superadmin can select a lab they belong to and enter one or more group of data according to the required format.
* A superadmin can create a new lab for any classes.
* A superadmin can view/modify/download data collected for the any labs.
* A superadmin can manage the class using this app.
* A superadmin can manage the accounts of admins.
General:
* Three group of users will be directed to different homepages when they log into the app. 
* Lower power group of users don't have access to the pages that higher power group of users use. 

##Part2 File Tree(partial)
```
.
├── LICENSE             - license for this app
├── Notes.md            - development notes
├── README.md           - this file
├── __main__.py         - the script used to run the app
├── config.cfg          - the app's configuration file
├── db_populate.py      - add initial values in to the database(mainly for testing)
├── db_reset.py         - reset and repopulate the database
├── error_log           - contains error log file
├── lemur
│   ├── __init__.py     - initialize the app and set up global variables
│   ├── static
│   │   ├── css         - contain css files for templates' decoration
│   │   └── js          - contain javascripts for templates, library, utility functions or global constants
│   ├── templates       - contains html templates
│   ├── utility.py      - utility functions used to make view functions in views.py more readable
│   └── views.py        - view functions for all the templates
├── migrations          - contains files for database migration
├── requirements.txt    - required modules/libraries for the app
├── run.py              - the script used to migrate/upgrade the database
└── unit_test.py        - unit test for the app
```
##Part3 Setup
###Step1 Create Virtual Environment for All Required Dependencies
``` mkvirtualenv lemur --python=python3```

###Step2 Install Required Packages
```
pip install -r requirements.txt
```

###Step3: Create Local Database
We’ll need to get a Postgres database set up to store our todo list. We’ll also add Python ORM SQLAlchemy to our app. Once you have Postgres installed, create a database and name it lemur to use as a local database. <br>
* Run PostgreSQL command line client.
* Create a database user with a password.
* Create two database instances(one for the app and the other for testing).

```
psql
create user zzy with password 'mypassword';
create database lemur owner zzy encoding 'utf-8'; 
create database lemur_test owner zzy encoding 'utf-8'; 
```

###Step4: Setup Database
In /lemur
```
python3 db_create
```

###Step5: Ask zhongzi@reed.edu for the private configuaration file
In order to run the latest version
You need to create a file named ’secret_key.cfg’ and put it into the root directory of the app
Its content should look like this
```
# Secret Key file
[key]
SECRET_KEY = AAA
STUDENT_API_URL = BBB
CLASS_API_URL = CCC
```

###Step6: Run the app `python3 __main__.py`


##Part4 Utility commands
###1: Reset databse
Warning: This command will drop all the tables of the database so all the data in the database will be lost.
```
python3 db_reset.py
```
###2: Initialize database
This command will populate the database with some examples. It is mainly for testing.
```
python3 db_populate.py
```
###3: Database migration
This will migrate the database's update and upgrade the database to the latest version of the database.
Warning: Not all changes are well supported by database migration(especially the change of a column's name will probably confuse the program). For details, please check out: [the official document for flask-migrate]:(http://flask-migrate.readthedocs.io/en/latest/)
```
python3 run.py db migrate
python3 run.py db upgrade
```
###4: Unit Testing
This will carry on a relatively comprehensive unit tests for the backend code.
```
python3 unit_test.py
```
