import os
import requests
from requests.auth import HTTPBasicAuth


def _get_jira_auth():
    """
    Internal helper to build Jira auth
    """
    return HTTPBasicAuth(
        os.getenv("JIRA_EMAIL"),
        os.getenv("JIRA_API_TOKEN")
    )


def get_my_jira_account_id():
    """
    Returns the accountId of the authenticated Jira user
    """
    url = f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/myself"
    resp = requests.get(url, auth=_get_jira_auth())
    resp.raise_for_status()
    return resp.json()["accountId"]


def get_jira_issues():
    """
    Demo-safe Jira issues fetcher.

    NOTE:
    Jira Cloud Free + team-managed projects have unreliable search indexing.
    Hence, for this assignment/demo, we fetch issues by key directly.
    """
    issue_keys = ["KAN-4"]  # demo issue keys
    issues = []

    for key in issue_keys:
        url = f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/issue/{key}"
        resp = requests.get(url, auth=_get_jira_auth())
        resp.raise_for_status()
        data = resp.json()

        issues.append({
            "key": data["key"],
            "summary": data["fields"]["summary"],
            "status": data["fields"]["status"]["name"]
        })

    return issues


