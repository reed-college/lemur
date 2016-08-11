# This script is used to run all the test files in the tests folder
import os


def run_tests():
    os.system('python3 test_integration_utility_generate_and_convert.py')
    os.system('python3 test_integration_utility_find_and_get.py')
    os.system('python3 test_integration_db_and_models.py')
    os.system('python3 test_integration_utility_modify.py')
    os.system('python3 test_integration_network.py')

if __name__ == '__main__':
    run_tests()
