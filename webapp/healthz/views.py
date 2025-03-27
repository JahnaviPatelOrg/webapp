import json
import time
import logging
import statsd
import boto3
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import HealthCheck
from django.db import OperationalError
from datetime import datetime

# Initialize logger
logger = logging.getLogger('webapp')

# Initialize CloudWatch Metrics Client
cloudwatch = boto3.client('cloudwatch', region_name="us-east-1")

# Initialize StatsD client
statsd_client = statsd.StatsClient('localhost', 8125)

@csrf_exempt
@require_http_methods(["GET"])
def healthz(request):
    start_time = time.time()  # Start API execution timer
    statsd_client.incr('api.healthz.calls')  # Increment API call counter

    # Reject if any payload exists
    if request.body or request.GET:
        #Record failed request API timing
        api_execution_time = (time.time() - start_time) * 1000
        statsd_client.timing('api.healthz.request.error.duration', api_execution_time)

        logger.warning(json.dumps({
            "level": "WARNING",
            "message": "Invalid request - payload detected",
            "endpoint": "/healthz",
            "method": "GET",
            "timestamp": datetime.utcnow().isoformat()
        }))
        return HttpResponse(status=400)

    # Ensure response is not cached
    response_headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'X-Content-Type-Options': 'nosniff'
    }

    try:
        # Database connectivity check
        db_start_time = time.time()
        with statsd_client.timer('database.health_check_time'):
            HealthCheck.objects.create()
        db_execution_time = (time.time() - db_start_time) * 1000  # Convert to ms

        logger.info(json.dumps({
            "level": "INFO",
            "message": "Health check successful",
            "endpoint": "/healthz",
            "method": "GET",
            "operation": "database_health_check",
            "db_execution_time_ms": db_execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }))
        # record database health check time
        statsd_client.timing('api.healthz.db.duration', db_execution_time)

        # Record API execution time with StatsD (in milliseconds)
        api_time = (time.time() - start_time) * 1000
        statsd_client.timing('api.healthz.duration', api_time)

        return HttpResponse(status=200, headers=response_headers)

    except OperationalError:
        # Record failed API timing
        api_execution_time = (time.time() - start_time) * 1000
        statsd_client.timing('api.healthz.error.duration', api_execution_time)

        logger.error(json.dumps({
            "level": "ERROR",
            "message": "Database connectivity failure",
            "endpoint": "/healthz",
            "method": "GET",
            "operation": "database_health_check",
            "timestamp": datetime.utcnow().isoformat()
        }))

        return HttpResponse(status=503, headers=response_headers)

    except Exception as e:
        # Record failed API timing for unexpected errors
        api_execution_time = (time.time() - start_time) * 1000
        statsd_client.timing('api.healthz.exception.duration', api_execution_time)

        logger.exception(json.dumps({
            "level": "ERROR",
            "message": "Unexpected error in health check",
            "error": str(e),
            "endpoint": "/healthz",
            "method": "GET",
            "operation": "database_health_check",
            "timestamp": datetime.utcnow().isoformat()
        }))

        return HttpResponse(status=503, headers=response_headers)
