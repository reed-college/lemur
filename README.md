# lemur
Bio data collector

## Part1 App General Description
This is a data collector for biology class.
It has three groups of users and corresponder powers. 
### Student: 
* A student can select a lab they belong to and enter one or more group of data according to the required format. 

### Admin:
* An admin can select a lab they belong to and enter one or more group of data according to the required format.
* An admin can create a new lab for their class.
* An admin can view/modify/download data collected for the labs they created.

### SuperAdmin:
* A superadmin can select a lab they belong to and enter one or more group of data according to the required format.
* A superadmin can create a new lab for any classes.
* A superadmin can view/modify/download data collected for the any labs.
* A superadmin can manage the class using this app.
* A superadmin can manage the accounts of admins.
General:
* Three group of users will be directed to different homepages when they log into the app. 
* Lower power group of users don't have access to the pages that higher power group of users use. 


## Part2 Setup
1. Create Virtual Environment for All Required Dependencies
` mkvirtualenv lemur --python=python3 `

2. Install Required Packages
` pip install -r requirements.txt `

3. Create Local Database
Set up a Postgres database. Add Python ORM SQLAlchemy to app. Once you have Postgres installed, create a database and name it lemur to use as a local database. 
* Run PostgreSQL command line client.
* Create a database user with a password.
* Create two database instances(one for the app and the other for testing).

Here is an example:

```
psql
create user zzy with password 'mypassword';
create database lemur owner zzy encoding 'utf-8'; 
create database lemur_test owner zzy encoding 'utf-8'; 
```

4. Setup Database
` python3 run.py db init `

5. (optional)You may want to set up database migration version
```
python3 run.py db migrate
python3 run.py db upgrade
```

6. (optional)You may want to populate the database

` 'python3 db_populate_real.py' `

7. Ask Reed College CIT for the private configuaration file
In order to run the app
You need to create a file named ’config.cfg’ and put it into both the root directory and the tests directory(for testing setup) of the app
Its content should look like the content in `config_example.cfg`(all the values need to be set up)


8. Run the app `python3 __main__.py`


## Part3 Utility commands
### 1: Reset databse
Warning: This command will drop all the tables of the database so all the data in the database will be lost.
` python3 db_reset.py `
### 2: Initialize database
This command will populate the database with some examples. It is mainly for testing.
` python3 db_populate.py `
### 3: Database migration
This will migrate the database's update and upgrade the database to the latest version of the database.
Warning: Not all changes are well supported by database migration(especially the change of a column's name will probably confuse the program). For details, please check out: [the official document for flask-migrate](http://flask-migrate.readthedocs.io/en/latest/)
```
python3 run.py db migrate
python3 run.py db upgrade
```
### 4: Testing
Tests for the backend code: ` python3 tests_script.py ` in lemur/lemur/tests

Tests for the frontend code: Use any main stream browser to open js_test.html in lemur/lemur/tests

