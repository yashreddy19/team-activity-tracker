from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ViewSet


class PingView(ViewSet):
    def ping(self, request):
        return Response({"success": True, "data": "pong"}, status=HTTP_200_OK)
