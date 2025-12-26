import requests


def get_github_activity(username):
    username = "yashreddy19"
    commits_url = f"https://api.github.com/search/commits?q=author:{username}"
    prs_url = f"https://api.github.com/search/issues?q=type:pr+author:{username}"

    commits = requests.get(commits_url).json().get("total_count", 0)
    prs = requests.get(prs_url).json().get("total_count", 0)

    return {"commits": commits, "pull_requests": prs}
