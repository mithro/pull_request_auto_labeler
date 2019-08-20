# pull_request_auto_labeler
Automatically label Github pull requests based on elements of the PR title. 
Default configuration expects Jira style ticket code(PROJ-100) in PR title

This labeler does the following:
 - get all open Pull Requests for all the repositories for an organization/user
 - check each PR to see if it has any matching a Jira style ticket code in the title (PROJ-100)
 - apply a label to the Pull Request matching the uppercase version of the project codes from the title (PROJ)

[![PyPI version](https://badge.fury.io/py/pull-request-auto-labeler.svg)](https://badge.fury.io/py/pull-request-auto-labeler)

## Installation
If you want to run this as a cron, you can install from pypi with pip:
`pip install pull-request-auto-labeler`

But if you're going to set this up as an AWS Lambda, you'll want the `serverless.yaml`, `serverless-requirements.txt` and `handler.py` so you might as well pull the source.

## Setup
Set the following enviornment vars:

- **[Required] GITHUB_API_TOKEN:** A Github API Token which has access to read the repositories you want 
and modify 
pull requests. 
If you don't have one you see the guide [here](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line)
- **[Required] ORGANIZATION:** the name of the github organization/username that you want to check PRs for.
- *[Optional] LABEL_EXTRACTING_REGEX:* Regex expression which will be applied on the PR title using python's
 `re.findall`. 
  - This regex expression should have one matching group which returns the portion of the title which
 should be used as a label. i.e. if the regex finds PROJ-100, the matching group should be PROJ
  - Since we're using `re.findall` this can have multiple matches on the title, but each
 match must have only one group.
  - Default is `\s*[\[]*([a-zA-Z0-9]{2,})[-|\s][0-9]+` which matches: `PROJ-100`, `[PROJ-100]`, `B2C-1`, `Proj 100`.

## Running from command line
`python auto_labeler.py`

## Running as a Cron on AWS Lambda

For convenience I've included setup instructions to run this as a cron using aws lambda made easy by the [serverless](https://serverless.com/framework/docs/) toolkit. If you haven't used serverless, I have a getting started with serverless guide [here](https://gist.github.com/markddavidoff/0bbfcdfc29bbbdedc8b57e062987b480) 

### Install serverless plugins
*serverless-python-requirements*

*Its pretty annoying to add external requirements to a lambda when deploying manually. You have to build the wheels
for the packages on an aws linux ami and include those in the zip that you upload. Luckily, there's a serverless plugin
to make that all super easy.*
```
sls plugin install -n serverless-python-requirements
```

### Setup serverless for this project
- Copy the `serverless.yaml`, `serverless-requirements.txt` and `handler.py` files in this repo to wherever you're using this, or simply download this repo and use that as your source 
- tweak any provider params you need to to match your setup
- Set the run frequency (update under `functions>lambdaCron>events>schedule`)

### Deploy to AWS
`sls deploy`
