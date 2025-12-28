class GitHubServiceUnavailable(Exception):
    """Raised when GitHub API fails after retries."""


class JiraServiceUnavailable(Exception):
    """Raised when Jira API fails after retries."""
