from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import HealthCheck
from django.db import OperationalError
from django.http import HttpResponse

@csrf_exempt
@require_http_methods(["GET"])
def healthz(request):
    # Reject if any payload exists
    if request.body or request.GET:
        return HttpResponse(status=400)

    # Ensure response is not cached
    response_headers = {'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache',
                        'X-Content-Type-Options': 'nosniff'}

    try:
        # Try inserting a record into the database
        HealthCheck.objects.create()
        return HttpResponse(status=200, headers=response_headers)
    except OperationalError:
        # Return 503 if database connection fails
        return HttpResponse(status=503, headers=response_headers)
    except Exception:
        # Return 503 if insertion fails
        return HttpResponse(status=503, headers=response_headers)
