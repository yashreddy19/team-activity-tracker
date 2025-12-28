from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth

from team_activity_tracker.settings import JIRA_ACCOUNT_ID, JIRA_API_TOKEN, JIRA_BASE_URL, JIRA_EMAIL

USER_ALIAS_TO_ACCOUNT_ID = {
    "john": JIRA_ACCOUNT_ID,
    "sarah": JIRA_ACCOUNT_ID,
    "mike": JIRA_ACCOUNT_ID,
}


def get_auth():
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)


def get_jira_activity(username: str, days: int = None):
    """
    Returns a list of Jira issues assigned to the user.

    Raises:
        ValueError: if user is not found
    """

    username_key = username.lower()

    if username_key not in USER_ALIAS_TO_ACCOUNT_ID:
        raise ValueError(f"User '{username}' not found")

    account_id = USER_ALIAS_TO_ACCOUNT_ID[username_key]

    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    payload = {
        "jql": f'assignee = "{account_id}"',
        "fields": ["summary", "status", "updated"],
        "maxResults": 50,
    }

    resp = requests.post(url, auth=get_auth(), json=payload)
    resp.raise_for_status()

    issues = resp.json().get("issues", [])

    # Filter by time window if required
    if days is not None:
        since = datetime.now() - timedelta(days=days)
        issues = [
            issue
            for issue in issues
            if datetime.strptime(issue["fields"]["updated"], "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None) >= since
        ]

    return [
        {
            "key": issue["key"],
            "summary": issue["fields"]["summary"],
            "status": issue["fields"]["status"]["name"],
            "updated": issue["fields"]["updated"],
        }
        for issue in issues
    ]
