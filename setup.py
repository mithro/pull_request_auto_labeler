import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='pull_request_auto_labeler',
    version='0.8',
    url='https://github.com/markddavidoff/pull_request_auto_labeler',
    author='Mark Davidoff',
    author_email='markddavidoff@gmail.com',
    description='Automatically label Github pull requests based on elements of the PR title. Expects Jira style ticket code(PROJ-100) in PR title',
    long_description=README,
    long_description_content_type="text/markdown",
    py_modules=['pull_request_auto_labeler'],
    license='MIT',
    install_requires=[
        'github3.py==1.2.0',
        'tqdm==4.33.0'
    ],
    entry_points='''
        [console_scripts]
        pull_request_auto_labeler=pull_request_auto_labeler:add_labels_for_project_names_from_pr_titles
    '''
)
