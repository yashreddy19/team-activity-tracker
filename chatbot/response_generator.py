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
    return jira_template(name, jira_data) + "\n\n" + github_template(name, github_data)
