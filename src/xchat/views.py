from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http.response import JsonResponse
import time


def test(request):
    return JsonResponse({'ok': True, 't': time.time()})


class TestView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        return Response({'ok': True, 't': time.time()})
