# lemur ![alt text](https://travis-ci.org/reed-college/lemur.svg?branch=master)
This is a data collector for collecting biology data. It's run on reed.lemur.edu(a subdomain of Reed College). It can only be accessed by Reed faculty/staff/students who have registered biology classes. However, you are welcome to mirror the code and host it on another server and use it whatever way you like.


## Part1 App Description
Lemur is an app built for efficient data consolidation from multiple independent sources. Classes with laboratory components that need to quickly collect data from all participants will benefit most. Consequently, there are three expected users of the app: lab instructors, professors, and students. Each of these corresponds to a different level of access. Lab instructors are considered Super Admins and are able to create, monitor, and edit the forms students submit data to. Additionally, they manage user access. Admins, or professors, are identical except that they cannot manage users. Students can only submit data. Professors that need to act as lab instructors should be given Super Admin status. 


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
create database travis_ci_test owner zzy encoding 'utf-8'; 
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
You need to create a file named ’config.cfg’ and put it into both the ` instance ` folder and ` lemur/tests ` folder
Its content should look like the content in `instance/config_example.cfg`(all the values need to be set up)
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
Tests for the backend code: ` nose2 ` in lemur/lemur/tests

Tests for the frontend code: Use any main stream browser to open js_test.html in lemur/lemur/tests

The app will be run and the backend tests will be run automatically when one pushs new changes to the app's github repo


## Part 4 User Guide
The Home page of each section links to the pages available to the user. Users can also move through the app using the sidebar, which appears when the Lemur logo in the upper lefthand corner of the page is clicked. 


### Admin Guide: 

**Create/Manage Lab**

Fill in the fields to create a new lab. The “Lab Instruction” field is optional and displays above the student entry form. Click submit to fill in the questions for the lab or reset to clear all fields. At the bottom of the page is a list of labs currently available for data collection or download. Each can be modified, duplicated or deleted. Duplication is useful for classes where labs are repeated each year. Labs can also be made “Download Only” or “Unavailable”. Unavailable labs are hidden from student access to prevent data entry before or after a lab session. “Download Only” labs are also hidden and allow the Admin to download collected data in jmp friendly file format on the “Manage/Retrieve Data” page.

**Manage/Retrieve Data**

After all students have submitted data and the lab is marked for download, navigate to the “Manage/Retrieve Data” page. Select the labs to download and click “Save All”, then hit “Download”. Labs containing identical questions (i.e. duplicate labs) can be combined by checking both boxes before hitting “Save All”. Once downloaded open the file in Jmp.

**Create/Manage User (Super Admin Only)**

Create new users by filling in the fields, selecting the appropriate user role, and clicking “Submit”. 

Edit a user's role by selecting/deselecting their user role in the drop down in the user's row in the user list table. Click the “Save” button to save the change you made. 

Delete a user by clicking the delete button at the end of the user's row in the user list table.

**Create/Manage Class (Super Admin Only)**

Create a new class by filling in the fields, selecting the class' professor(s) and student(s).

Add/delete students/professors to a class by selecting/deselecting their names in the dropdown in the class's row in the class list table. Click the “Save” button to save the change you made. 

Delete a class by clicking the delete button at the end of the class's row in the class list table.

Enter Data For Lab 

Admins have access to the student data-entry page so they can review what students will see and can enter data for student groups when needed. Under the lab list select the desired lab and click the button to go to that page. Fill in the entry fields on the lab page and click submit to add data. Using the reset button will clear all data. The “Add a new data entry” button creates a duplicate entry field for each question. Duplicate fields are intended for inputting additional trials. 


### Student Guide: 

Navigate to the app page and click “Enter Data for Lab” to see labs available for data collection. Select the appropriate lab and fill in the fields with your data. If you have multiple trials select “Add a new data entry” at the bottom of the page to create fields for your trials. Use the reset button to clear all fields or click submit to check/submit your data. A pop-up will show up to tell you whether your data looks good(according to the criteria of that entry set up by the lab instrutor). You can communicate with the instructor about the stange data you get; however, you can still submit the strange data forcefully.

## Part 5 Sample Pages
SuperAdmin Homepage
<img width="1308" alt="superadmin_homepage" src="https://cloud.githubusercontent.com/assets/12670254/19320854/d2bf815c-9067-11e6-8a4d-e7f383446747.png">

Admin Manage Lab Page
<img width="1297" alt="admin_create_lab_page" src="https://cloud.githubusercontent.com/assets/12670254/19320856/d71e021e-9067-11e6-9adc-2ecb8a1f0f38.png">

Admin Edit Lab Page
<img width="1296" alt="admin_edit_lab_page" src="https://cloud.githubusercontent.com/assets/12670254/19320860/dd3ceb24-9067-11e6-8719-f865929d904f.png">

Student Data Entry Page
<img width="1312" alt="student_enter_data_page" src="https://cloud.githubusercontent.com/assets/12670254/19320865/df7d0068-9067-11e6-894b-7adba9eb7563.png">

Admin Data Collection Page
<img width="1314" alt="admin_data_collection_page" src="https://cloud.githubusercontent.com/assets/12670254/19320867/e07f920a-9067-11e6-9ce9-cf1df2036ec6.png">
