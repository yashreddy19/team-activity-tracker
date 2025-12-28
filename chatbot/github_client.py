import requests

GITHUB_USERNAME_MAP = {
    "john": "yashreddy19",
    "sarah": "yashreddy19",
    "mike": "yashreddy19",
}


def get_headers(for_commits=False):
    headers = {}
    if for_commits:
        headers["Accept"] = "application/vnd.github.cloak-preview+json"

    return headers


def get_github_activity(name):
    key = name.lower()
    if key not in GITHUB_USERNAME_MAP:
        raise ValueError(f"GitHub user '{name}' not found")

    username = GITHUB_USERNAME_MAP[key]

    commits_url = "https://api.github.com/search/commits"
    prs_url = "https://api.github.com/search/issues"

    commits_resp = requests.get(commits_url, headers=get_headers(for_commits=True), params={"q": f"author:{username}"})
    commits_resp.raise_for_status()

    prs_resp = requests.get(prs_url, headers=get_headers(), params={"q": f"type:pr author:{username}"})
    prs_resp.raise_for_status()

    return {
        "commits": commits_resp.json().get("total_count", 0),
        "pull_requests": prs_resp.json().get("total_count", 0),
    }


from datetime import datetime, timedelta, timezone


def get_recent_commits(name, days=None, limit=20):
    key = name.lower()
    if key not in GITHUB_USERNAME_MAP:
        raise ValueError(f"GitHub user '{name}' not found")

    username = GITHUB_USERNAME_MAP[key]

    url = "https://api.github.com/search/commits"
    params = {
        "q": f"author:{username}",
        "sort": "author-date",
        "order": "desc",
        "per_page": limit,
    }

    resp = requests.get(url, headers=get_headers(for_commits=True), params=params)
    resp.raise_for_status()

    commits = []
    since = None

    if days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=days)

    for item in resp.json().get("items", []):
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


def get_active_pull_requests(name):
    key = name.lower()
    if key not in GITHUB_USERNAME_MAP:
        raise ValueError(f"GitHub user '{name}' not found")

    username = GITHUB_USERNAME_MAP[key]

    url = "https://api.github.com/search/issues"
    params = {"q": f"type:pr author:{username} state:open"}

    resp = requests.get(url, headers=get_headers(), params=params)
    resp.raise_for_status()

    return [
        {
            "title": pr["title"],
            "repo": pr["repository_url"].split("repos/")[-1],
            "url": pr["html_url"],
        }
        for pr in resp.json().get("items", [])
    ]


def get_recent_repositories(name, limit=5):
    key = name.lower()
    if key not in GITHUB_USERNAME_MAP:
        raise ValueError(f"GitHub user '{name}' not found")

    username = GITHUB_USERNAME_MAP[key]

    url = "https://api.github.com/search/commits"
    params = {
        "q": f"author:{username}",
        "sort": "author-date",
        "order": "desc",
    }

    resp = requests.get(url, headers=get_headers(for_commits=True), params=params)
    resp.raise_for_status()

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
