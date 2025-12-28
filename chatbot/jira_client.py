from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from requests.auth import HTTPBasicAuth
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from chatbot.constants import JIRA_USERNAME_TO_ACCOUNT_ID_MAP
from chatbot.exceptions import JiraServiceUnavailable
from team_activity_tracker.settings import JIRA_API_TOKEN, JIRA_BASE_URL, JIRA_EMAIL


def get_auth():
    return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)


def is_retryable_http_error(exception: Exception) -> bool:
    """
    Retry only for HTTP 5xx errors.
    """
    if isinstance(exception, requests.exceptions.HTTPError):
        response = exception.response
        return response is not None and 500 <= response.status_code < 600
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(3),
    retry=retry_if_exception(is_retryable_http_error),
    reraise=True,
)
def fetch_jira_issues(url: str, payload: dict) -> requests.Response:
    resp = requests.post(
        url,
        auth=get_auth(),
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    return resp


def get_jira_activity(username: str, days: int = None) -> List[Dict[str, Any]]:
    """
    Returns a list of Jira issues assigned to the user.

    Raises:
        ValueError: if user is not found
        JiraServiceUnavailable: if Jira API fails after retries
    """

    username_key = username.lower()

    if username_key not in JIRA_USERNAME_TO_ACCOUNT_ID_MAP:
        raise ValueError(f"User '{username}' not found")

    account_id = JIRA_USERNAME_TO_ACCOUNT_ID_MAP[username_key]

    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    payload = {
        "jql": f'assignee = "{account_id}"',
        "fields": ["summary", "status", "updated"],
        "maxResults": 50,
    }

    try:
        resp = fetch_jira_issues(url, payload)
    except requests.exceptions.HTTPError as e:
        raise JiraServiceUnavailable("Jira is temporarily unavailable") from e

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
