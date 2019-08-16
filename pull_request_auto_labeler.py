import os
import re
import sys

from github3 import login

try:
    GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
    ORGANIZATION = os.environ['ORGANIZATION']
except KeyError as error:
    sys.stderr.write('Please set the environment variable {0}'.format(error))
    sys.exit(1)


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


# PROJECT-100, [project2-900], etc
RE_TICKET_CODE = re.compile(r'\s*[\[]*([a-zA-Z][a-zA-Z0-9]*[-][0-9][0-9]*)')

MISSING_PROJECT_NAME_LABEL = 'NO JIRA TICKET'


def get_ticket_codes_from_issue(issue):
    # PROJECT-100, project2-900, etc
    return RE_TICKET_CODE.findall(issue.title)


def get_project_names(issue):
    # PROJECT1, PROJECT2
    ticket_codes = get_ticket_codes_from_issue(issue)
    return [code.split('-')[0].upper() for code in ticket_codes]


def add_labels_for_project_names_from_pr_titles():
    client = login(token=GITHUB_API_TOKEN)
    organization = client.organization(ORGANIZATION)
    for repository in organization.repositories():
        issues_that_are_prs = get_issues_that_are_prs(repository)
        for issue in issues_that_are_prs:
            project_names = get_project_names(issue)
            if project_names:
                issue.add_labels(*project_names)
            elif MISSING_PROJECT_NAME_LABEL:
                issue.add_labels(MISSING_PROJECT_NAME_LABEL)


def lambda_handler(event, context):
    add_labels_for_project_names_from_pr_titles()
    response = {
        "statusCode": 200,
        "body": "OK"
    }

    return response


if __name__ == '__main__':
    add_labels_for_project_names_from_pr_titles()
