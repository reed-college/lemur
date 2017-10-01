# This script is used to reset(drop and create)
import os
import sys
sys.path.append('..')

# If you already have code for dropping the DB, why not have code for creating
# the DB in the first place? -- RMD 2017-08-26

def reset_database():
    os.system('dropdb lemur')
    os.system('createdb lemur')
    os.system('rm -r migrations')
    os.system('python3 run.py db init')
    os.system('python3 run.py db migrate')
    os.system('python3 run.py db upgrade')
    os.system('python3 db_populate_real.py')

if __name__ == '__main__':
    reset_database()
