import os
from flake8.api import legacy as f8
import re

heredir = os.path.abspath(os.path.dirname(__file__))
celery_jobs_directory = os.path.join(heredir, '../../celeryutils')
laiutils_directory = os.path.join(heredir, '../../laiutils')
unit_tests_directory = os.path.join(heredir, '../unit')
runner_directory = os.path.join(heredir, '../../')

testable_dirs = [heredir, celery_jobs_directory, laiutils_directory,
                 unit_tests_directory, runner_directory]


def flake8_examine(file_loc):
    style_guide = f8.get_style_guide()
    result = style_guide.check_files([file_loc])
    error_count = result.total_errors
    return error_count


def get_all_py_files(directory):
    pyfiles = []
    pattern = ".*py$"
    for f in os.listdir(directory):
        fullpath = os.path.join(directory, f)
        if (os.path.isfile(fullpath) and re.match(pattern, f)):
            pyfiles.extend([fullpath])
    return pyfiles


class TestFlake8:
    def test_flake8(self):
        to_test = []
        for x in testable_dirs:
            to_test.extend(get_all_py_files(x))
        for f in to_test:
            assert flake8_examine(f) == 0
