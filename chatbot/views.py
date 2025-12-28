# Create your views here.

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ViewSet

from .github_client import get_active_pull_requests, get_github_activity, get_recent_commits, get_recent_repositories
from .jira_client import get_jira_activity
from .query_parser import extract_name_and_intent
from .response_generator import (
    combined_template,
    github_commits_template,
    github_prs_template,
    github_repos_template,
    github_template,
    jira_template,
)
from .serializers import ChatbotSerializer


class ChatbotView(ViewSet):
    def post(self, request):
        serializer = ChatbotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Invalid payload", "errors": serializer.errors},
                status=HTTP_400_BAD_REQUEST,
            )

        message = serializer.validated_data["message"]
        name, intent, days = extract_name_and_intent(message)

        if not name:
            return Response({"success": False, "message": "User not found"}, status=HTTP_400_BAD_REQUEST)

        jira_data = []
        github_data = {}

        if intent in ["JIRA_ONLY", "BOTH"]:
            try:
                jira_data = get_jira_activity(name, days)
            except ValueError as e:
                return Response({"success": False, "errors": [str(e)]}, status=HTTP_400_BAD_REQUEST)

        if intent == "JIRA_ONLY":
            response = jira_template(name, jira_data)

        elif intent == "GITHUB_COMMITS":
            data = get_recent_commits(name, days)
            response = github_commits_template(name, data)

        elif intent == "GITHUB_PRS":
            data = get_active_pull_requests(name)
            response = github_prs_template(name, data)

        elif intent == "GITHUB_REPOS":
            data = get_recent_repositories(name)
            response = github_repos_template(name, data)

        elif intent == "GITHUB_ONLY":
            github_data = get_github_activity(name)
            response = github_template(name, github_data)

        elif intent == "BOTH":
            github_data = get_recent_commits(name, days)
            response = combined_template(name, jira_data, github_data)

        else:
            return Response({"success": False, "errors": ["Unsupported intent"]}, status=HTTP_400_BAD_REQUEST)

        return Response({"success": True, "data": response}, status=HTTP_200_OK)
