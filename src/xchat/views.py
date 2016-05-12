from django.http.response import JsonResponse
import time


def test(request):
    return JsonResponse({'ok': True, 't': time.time()})