from django.urls import path
from django.http import JsonResponse

# simple test view (so you can hit /api/edi/ping/ and see a response)
def ping_view(request):
    return JsonResponse({"status": "ok", "message": "EDI app alive"})

urlpatterns = [
    path("ping/", ping_view, name="edi-ping"),
]
