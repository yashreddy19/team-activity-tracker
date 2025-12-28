def jira_template(name, issues):
    if not issues:
        return f"No JIRA issues found for {name}."

    lines = [f"{name} is working on {len(issues)} JIRA issue(s):"]
    for i in issues:
        lines.append(f"- {i['key']} ({i['status']}): {i['summary']}")
    return "\n".join(lines)


def github_template(name, data):
    return f"On GitHub, {name} has:\n" f"- {data['commits']} commits\n" f"- {data['pull_requests']} open pull requests"


def combined_template(name, jira_data, github_data):
    return jira_template(name, jira_data) + "\n\n" + github_commits_template(name, github_data)


def github_commits_template(name, commits):
    if not commits:
        return f"No recent GitHub commits found for {name}."

    lines = [f"Recent GitHub commits by {name}:"]
    for c in commits:
        lines.append(f"- {c['repo']}: {c['message']}")
    return "\n".join(lines)


def github_prs_template(name, prs):
    if not prs:
        return f"No active pull requests found for {name}."

    lines = [f"Active pull requests by {name}:"]
    for pr in prs:
        lines.append(f"- {pr['repo']}: {pr['title']}")
    return "\n".join(lines)


def github_repos_template(name, repos):
    if not repos:
        return f"No recent repository contributions found for {name}."

    lines = [f"Repositories recently contributed to by {name}:"]
    for repo in repos:
        lines.append(f"- {repo}")
    return "\n".join(lines)
