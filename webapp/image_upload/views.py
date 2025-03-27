import logging
import time
import boto3
import watchtower
import os
import uuid
import json
from datetime import datetime
import statsd
from decouple import config
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.db import DatabaseError, OperationalError
from .models import Image

# Initialize logging
logger = logging.getLogger('webapp')

# Initialize CloudWatch Metrics Client
cloudwatch = boto3.client('cloudwatch', region_name=config('AWS_REGION_NAME', default="us-east-1"))

# Initialize StatsD client
statsd_client = statsd.StatsClient('localhost', 8125)

# AWS S3
s3_client = boto3.client('s3')
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', config('S3_BUCKET_NAME'))


def upload_image(request):
    start_time = time.time()  # Start timer for API execution

    # Increment API call counter with StatsD
    statsd_client.incr('api.upload_image.calls')

    if request.method == 'POST':
        if request.FILES.get('profilePic'):
            try:
                image = request.FILES['profilePic']
                image_id = str(uuid.uuid4())
                file_name = image.name
                upload_date = datetime.utcnow().strftime("%Y-%m-%d")
                file_path = f"{image_id}/{file_name}"
                # Structured logging
                logger.info(json.dumps({
                    "level": "INFO",
                    "message": f"Uploading image {file_name} to S3.",
                    "file_name": file_name,
                    "operation": "s3_upload",
                    "endpoint": "/upload-image",
                    "method": "POST",
                    "timestamp": datetime.utcnow().isoformat()
                }))

                # S3 upload with timing
                s3_upload_start = time.time()
                with statsd_client.timer('s3.upload_time'):
                    s3_client.upload_fileobj(image, BUCKET_NAME, file_path,
                                             ExtraArgs={
                                                 'Metadata': {
                                                     'upload_date': upload_date,
                                                     'filename': file_name,
                                                     'file_type': image.content_type,
                                                     'file_path': file_path,
                                                     'file_id': image_id
                                                 }})
                s3_upload_time = (time.time() - s3_upload_start) * 1000  # Convert to ms

                s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_path}"

                # Save to database with timing
                db_start_time = time.time()
                try:
                    with statsd_client.timer('database.save_time'):
                        image_record = Image.objects.create(id=image_id, file_name=file_name,
                                                            upload_date=upload_date, url=s3_url)
                except (DatabaseError, OperationalError) as db_error:
                    logger.error(json.dumps({
                        "level": "ERROR",
                        "message": "Database error occurred.",
                        "error": str(db_error),
                        "operation": "database_save",
                        "endpoint": "/upload-image",
                        "method": "POST",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_path)
                    return JsonResponse({"error": "Database error. Please try again later."}, status=503)
                db_execution_time = (time.time() - db_start_time) * 1000
                # Structured logging for success
                logger.info(json.dumps({
                    "level": "INFO",
                    "message": f"Image {file_name} uploaded successfully.",
                    "file_name": file_name,
                    "image_id": image_id,
                    "operation": "upload_success",
                    "endpoint": "/upload-image",
                    "method": "POST",
                    "timestamp": datetime.utcnow().isoformat()
                }))



                # Record S3 upload time with StatsD
                statsd_client.timing('s3.upload_image.duration', s3_upload_time)

                # Record database save time with StatsD
                statsd_client.timing('database.save_image.duration', db_execution_time)

                # Record API execution time with StatsD
                api_time = (time.time() - start_time) * 1000
                statsd_client.timing('api.upload_image.duration', api_time)

                return JsonResponse({
                    "file_name": file_name,
                    "id": image_id,
                    "url": s3_url,
                    "upload_date": upload_date,
                    "image_type": image.content_type
                }, status=201)
            except Exception as e:
                logger.exception(json.dumps({
                    "level": "ERROR",
                    "message": "Error uploading image.",
                    "error": str(e),
                    "operation": "upload_failure",
                    "endpoint": "/upload-image",
                    "method": "POST",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                return JsonResponse({"error": str(e)}, status=503)

        logger.warning(json.dumps({
            "level": "WARNING",
            "message": "Bad request: Missing image file.",
            "operation": "validate_request",
            "endpoint": "/upload-image",
            "method": "POST",
            "timestamp": datetime.utcnow().isoformat()
        }))
        return JsonResponse({"error": "Bad Request"}, status=400)

    logger.warning(json.dumps({
        "level": "ERROR",
        "message": "Method Not Allowed.",
        "operation": "validate_request",
        "endpoint": "/upload-image",
        "method": "POST",
        "timestamp": datetime.utcnow().isoformat()
    }))
    return JsonResponse({"error": "Method Not Allowed"}, status=405)


def handle_image(request, image_id=None):
    start_time = time.time()  # API timer
    endpoint = f"/v1/file/{image_id}"
    method = request.method
    if request.method == 'GET':
        statsd_client.incr('api.get_image.calls')
    elif request.method == 'DELETE':
        statsd_client.incr('api.delete_image.calls')

    if not image_id:
        logger.warning(json.dumps({
            "level": "WARNING",
            "message": "Bad request: Missing image_id",
            "operation": "validate_request",
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return JsonResponse({"error": "Bad Request"}, status=400)

    try:
        uuid_obj = uuid.UUID(image_id)
    except ValueError:
        logger.warning(json.dumps({
            "level": "WARNING",
            "message": f"Invalid UUID format: {image_id}",
            "operation": "validate_uuid",
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return JsonResponse({"error": "Invalid UUID"}, status=400)

    try:
        if request.method == 'GET':
            logger.info(json.dumps({
                "level": "INFO",
                "message": f"Fetching image with ID {image_id}.",
                "operation": "fetch_image",
                "endpoint": endpoint,
                "method": method,
                "timestamp": datetime.utcnow().isoformat()
            }))
            db_start_time = time.time()

            with statsd_client.timer('database.query_time'):
                image_record = Image.objects.get(id=image_id)

            db_execution_time = (time.time() - db_start_time) * 1000

            # TODO check time in console logs if roudoff is happening its crt and match with data in metrics
            # Record API execution time with StatsD
            api_time = (time.time() - start_time) * 1000
            statsd_client.timing('api.get_image.duration', api_time)

            return JsonResponse({
                "file_name": image_record.file_name,
                "id": image_record.id,
                "url": image_record.url,
                "upload_date": image_record.upload_date
            }, status=200)

        elif request.method == 'DELETE':
            logger.info(json.dumps({
                "level": "INFO",
                "message": f"Deleting image with ID {image_id}.",
                "operation": "delete_image",
                "endpoint": endpoint,
                "method": method,
                "timestamp": datetime.utcnow().isoformat()
            }))

            with statsd_client.timer('database.query_time'):
                image_record = Image.objects.get(id=image_id)

            file_key = image_record.url.split(f"{BUCKET_NAME}.s3.amazonaws.com/")[1]

            with statsd_client.timer('s3.delete_time'):
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)

            with statsd_client.timer('database.delete_time'):
                image_record.delete()

            #  Record S3 delete time with StatsD
            statsd_client.timing('s3.delete_image.duration', (time.time() - start_time) * 1000)

            # Record API execution time with StatsD
            api_time = (time.time() - start_time) * 1000
            statsd_client.timing('api.delete_image.duration', api_time)

            return JsonResponse({}, status=204)

        else:
            return JsonResponse({"error": "Method Not Allowed"}, status=405)

    except Image.DoesNotExist:
        logger.error(json.dumps({
            "level": "ERROR",
            "message": f"Image with ID {image_id} not found.",
            "operation": "fetch_image",
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return JsonResponse({"error": "Not Found"}, status=404)
    except (DatabaseError, OperationalError):
        logger.error(json.dumps({
            "level": "ERROR",
            "message": "Database error occurred.",
            "error": str(e),
            "operation": "database_query",
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return JsonResponse({"error": "Database error. Please try again later."}, status=503)
    except Exception as e:
        logger.exception(json.dumps({
            "level": "ERROR",
            "message": "Unexpected error occurred.",
            "error": str(e),
            "operation": "unknown_error",
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat()
        }))
        return JsonResponse({"error": str(e)}, status=503)