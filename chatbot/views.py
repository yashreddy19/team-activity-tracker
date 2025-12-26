# Create your views here.

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ViewSet

from .github_client import get_github_activity
from .jira_client import get_jira_activity
from .query_parser import extract_name_and_intent
from .response_generator import combined_template, github_template, jira_template
from .serializers import ChatbotSerializer


class ChatbotView(ViewSet):
    def post(self, request):
        serializer = ChatbotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=HTTP_400_BAD_REQUEST)
        message = serializer.validated_data["message"]

        name, intent = extract_name_and_intent(message)

        if not name:
            return Response({"success": False, "errors": ["User not found in query."]}, status=HTTP_400_BAD_REQUEST)

        jira_data = []
        github_data = {}

        if intent in ["JIRA_ONLY", "BOTH"]:
            jira_data = get_jira_activity(name)

        if intent in ["GITHUB_ONLY", "BOTH"]:
            github_data = get_github_activity(name)

        if intent == "JIRA_ONLY":
            response = jira_template(name, jira_data)
        elif intent == "GITHUB_ONLY":
            response = github_template(name, github_data)
        else:
            response = combined_template(name, jira_data, github_data)

        return Response({"success": True, "data": response}, status=HTTP_200_OK)
