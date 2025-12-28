import re


def extract_name_and_intent(message: str):
    msg = message.lower()

    name_match = re.search(r"\b(john|sarah|mike)\b", msg)
    name = name_match.group(0).capitalize() if name_match else None

    # Jira intent
    if any(word in msg for word in ["jira", "ticket", "issue"]):
        intent = "JIRA_ONLY"

    # GitHub-specific intents
    elif any(word in msg for word in ["commit", "commits"]):
        intent = "GITHUB_COMMITS"

    elif any(word in msg for word in ["pull request", "pull requests", "pr", "prs"]):
        intent = "GITHUB_PRS"

    elif any(word in msg for word in ["repo", "repos", "repository", "repositories"]):
        intent = "GITHUB_REPOS"

    # Generic GitHub intent
    elif "github" in msg:
        intent = "GITHUB_ONLY"

    # Fallback (both systems)
    else:
        intent = "BOTH"

    if "this month" in msg:
        days = 30
    elif "this week" in msg:
        days = 7
    elif "today" in msg:
        days = 1
    elif "recent" in msg or "these days" in msg:
        days = 3
    else:
        days = None

    return name, intent, days
