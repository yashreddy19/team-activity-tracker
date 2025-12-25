import os
import requests
from requests.auth import HTTPBasicAuth

def get_jira_issues(username):
    url = f"{os.getenv('JIRA_BASE_URL')}/rest/api/3/search"
    auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))

    jql = f'assignee = "{username}"'
    params = {"jql": jql}

    resp = requests.get(url, auth=auth, params=params)
    resp.raise_for_status()

    issues = []
    for issue in resp.json().get("issues", []):
        issues.append({
            "key": issue["key"],
            "summary": issue["fields"]["summary"],
            "status": issue["fields"]["status"]["name"]
        })

    return issues
