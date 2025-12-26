import re


def extract_name_and_intent(message: str):
    msg = message.lower()

    name_match = re.search(r"\b(john|sarah|mike)\b", msg)
    name = name_match.group(0).capitalize() if name_match else None

    if any(word in msg for word in ["jira", "ticket", "issue"]):
        intent = "JIRA_ONLY"
    elif any(word in msg for word in ["commit", "pull request", "github"]):
        intent = "GITHUB_ONLY"
    else:
        intent = "BOTH"

    return name, intent
