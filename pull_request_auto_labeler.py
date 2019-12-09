#!python3
import logging
import os
import re
import sys

from tqdm import tqdm
from github3 import login

try:
    GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
    ORGANIZATION = os.environ['ORGANIZATION']
    # PROJECT-100, [project2-900], etc
    LABEL_EXTRACTING_REGEX = os.environ.get('LABEL_EXTRACTING_REGEX',r'\s*[\[]*([a-zA-Z0-9]{2,})[-|\s][0-9]+')
except KeyError as error:
    sys.stderr.write('Please set the environment variable {0}'.format(error))
    sys.exit(1)

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_issues_that_are_prs(repository):
    # GitHub's REST API v3 considers every pull request an issue, but not every issue is a pull request.
    # For this reason, "Issues" endpoints may return both issues and pull requests in the response.
    # You can identify pull requests by the pull_request key.
    # In order to access labels we have to treat pull requests as issues
    issues_that_are_prs = []
    for issue in repository.issues(state='open', sort='created'):
        if issue.pull_request_urls:
            issues_that_are_prs.append(issue)
    return issues_that_are_prs


RE_TICKET_CODE = re.compile(LABEL_EXTRACTING_REGEX)

MISSING_PROJECT_NAME_LABEL = 'kokoro:force-run'

def label_events(issue):
    events = []
    for e in issue.events():
        if 'labeled' not in e.event:
            continue
        events.append((e.event, e.label['name']))
    return tuple(events)


def has_kokoro(label_events):
    for e, l in label_events:
        if 'kokoro' in l:
            return True
    return False


def add_labels_for_project_names_from_pr_titles(show_progress_bar=True):
    client = login(token=GITHUB_API_TOKEN)
    organization = client.organization(ORGANIZATION)
    repos_iterator = organization.repositories()
    log = logger.info
    if show_progress_bar:
        log = tqdm.write
        repos_iterator = tqdm(list(repos_iterator), desc=f'Repos in {ORGANIZATION}')
    log(f"Getting all repos in {ORGANIZATION}...")
    for repository in repos_iterator:
        issues_that_are_prs = get_issues_that_are_prs(repository)
        if show_progress_bar:
            issues_that_are_prs = tqdm(issues_that_are_prs, desc=f'PRs in   {repository.full_name}')

        log(f"Getting all PRs in {repository.full_name}...")
        for issue in issues_that_are_prs:
            if issue.user.login != "dependabot-preview[bot]":
                continue
            ev = label_events(issue)
            if has_kokoro(ev) and issue.number != 1160:
                log(f'{issue.user} Not updating PR {issue.number}-{issue.title}.')
            else:
                log(f'{issue.user}     Updating PR {issue.number}-{issue.title}.')
                issue.add_labels('kokoro:force-run')
                break


def lambda_handler(event, context):
    add_labels_for_project_names_from_pr_titles(show_progress_bar=False)
    response = {
        "statusCode": 200,
        "body": "OK"
    }

    return response


if __name__ == '__main__':
    add_labels_for_project_names_from_pr_titles()
