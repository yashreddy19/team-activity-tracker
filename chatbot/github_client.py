from datetime import datetime, timedelta, timezone
from multiprocessing.dummy import Pool as ThreadPool
from typing import Dict, List

import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from chatbot.constants import GITHUB_USER_ALIAS_TO_USERNAME_MAP
from chatbot.exceptions import GitHubServiceUnavailable
from team_activity_tracker.settings import GITHUB_BASE_URL


def is_retryable_github_error(exception: Exception) -> bool:
    """
    Retry only for HTTP 5xx errors from GitHub.
    """
    if isinstance(exception, requests.exceptions.HTTPError):
        response = exception.response
        return response is not None and 500 <= response.status_code < 600
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(3),
    retry=retry_if_exception(is_retryable_github_error),
    reraise=True,
)
def fetch_github_data(url: str, headers=None, params=None) -> requests.Response:
    resp = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp


def fetch_commits_count(username: str) -> int:
    url = f"{GITHUB_BASE_URL}/search/commits"
    resp = fetch_github_data(
        url,
        params={"q": f"author:{username}"},
    )
    return resp.json().get("total_count", 0)


def fetch_prs_count(username: str) -> int:
    url = f"{GITHUB_BASE_URL}/search/issues"
    resp = fetch_github_data(
        url,
        params={"q": f"type:pr author:{username}"},
    )
    return resp.json().get("total_count", 0)


def get_github_activity(name: str) -> Dict[str, int]:
    username = GITHUB_USER_ALIAS_TO_USERNAME_MAP[name.lower()]

    try:
        with ThreadPool(processes=2) as pool:
            commits_count, prs_count = pool.map(
                lambda fn: fn(username),
                [fetch_commits_count, fetch_prs_count],
            )
    except requests.exceptions.HTTPError as e:
        raise GitHubServiceUnavailable("Github is temporarily unavailable") from e

    return {
        "commits": commits_count,
        "pull_requests": prs_count,
    }


def get_recent_commits(name: str, days: int = None, limit: int = 20) -> List[Dict]:
    username = GITHUB_USER_ALIAS_TO_USERNAME_MAP[name.lower()]

    url = f"{GITHUB_BASE_URL}/search/commits"
    params = {
        "q": f"author:{username}",
        "sort": "author-date",
        "order": "desc",
        "per_page": limit,
    }

    try:
        resp = fetch_github_data(
            url,
            params=params,
        )
    except requests.exceptions.HTTPError as e:
        raise GitHubServiceUnavailable("Github is temporarily unavailable") from e

    items = resp.json().get("items", [])

    since = None
    if days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=days)

    commits = []
    for item in items:
        commit_date = datetime.fromisoformat(item["commit"]["author"]["date"].replace("Z", "+00:00"))

        if since and commit_date < since:
            continue

        commits.append(
            {
                "repo": item["repository"]["full_name"],
                "message": item["commit"]["message"],
                "date": item["commit"]["author"]["date"],
            }
        )

    return commits


def get_active_pull_requests(name: str) -> List[Dict]:
    username = GITHUB_USER_ALIAS_TO_USERNAME_MAP[name.lower()]

    url = f"{GITHUB_BASE_URL}/search/issues"
    params = {"q": f"type:pr author:{username} state:open"}

    try:
        resp = fetch_github_data(
            url,
            params=params,
        )
    except requests.exceptions.HTTPError as e:
        raise GitHubServiceUnavailable("Github is temporarily unavailable") from e

    return [
        {
            "title": pr["title"],
            "repo": pr["repository_url"].split("repos/")[-1],
            "url": pr["html_url"],
        }
        for pr in resp.json().get("items", [])
    ]


def get_recent_repositories(name: str, limit: int = 5) -> List[str]:
    username = GITHUB_USER_ALIAS_TO_USERNAME_MAP[name.lower()]

    url = f"{GITHUB_BASE_URL}/search/commits"
    params = {
        "q": f"author:{username}",
        "sort": "author-date",
        "order": "desc",
    }

    try:
        resp = fetch_github_data(
            url,
            params=params,
        )
    except requests.exceptions.HTTPError as e:
        raise GitHubServiceUnavailable("Github is temporarily unavailable") from e

    repos = []
    seen = set()

    for item in resp.json().get("items", []):
        repo = item["repository"]["full_name"]
        if repo not in seen:
            seen.add(repo)
            repos.append(repo)
        if len(repos) >= limit:
            break

    return repos
