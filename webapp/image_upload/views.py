from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from .models import Image
from django.conf import settings
import os
import uuid
from datetime import datetime
from decouple import config
import boto3

s3_client = boto3.client('s3')
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', config('S3_BUCKET_NAME'))

def upload_image(request):
    if request.method == 'POST' :
        if request.FILES.get('profilePic'):
            image = request.FILES['profilePic']
            image_id = str(uuid.uuid4())
            file_name = image.name
            upload_date = datetime.utcnow().strftime("%Y-%m-%d")
            file_path = f"{image_id}/{file_name}"

            # Upload to S3
            s3_client.upload_fileobj(image, BUCKET_NAME, file_path,
                                     ExtraArgs={
                'Metadata': {
                    'upload_date': upload_date,
                    'filename': file_name,
                    'file_type': image.content_type,
                    'file_path': file_path,
                    'dile_id': image_id
                }})
            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_path}"
            print(file_name)
            # Save URL to RDS
            image_record = Image.objects.create(id=image_id,file_name=file_name,upload_date=upload_date,url=s3_url)

            return JsonResponse({
                "file_name": file_name,
                "id": image_id,
                "url": s3_url,
                "upload_date": upload_date,
                "image_type": image.content_type
            }, status=201)
        return JsonResponse({"error": "Bad Request"}, status=400)
    if request.method == 'GET' or request.method == 'DELETE':
        return JsonResponse({"error": "Bad Request"}, status=400)
    return JsonResponse({"error": "Method Not Allowed."}, status=405)


def handle_image(request, image_id=None):
    if not image_id:
        return JsonResponse({"error": "Bad Request"}, status=400)
    
    try:
        uuid_obj = uuid.UUID(image_id)
    except ValueError:
        return JsonResponse({"error": "Invalid UUID"}, status=400)

    if request.method == 'GET':
        try:
            image_record = Image.objects.get(id=image_id)
            return JsonResponse({
                "file_name": image_record.file_name,
                "id": image_record.id,
                "url": image_record.url,
                "upload_date": image_record.upload_date
            }, status=200)
        except Image.DoesNotExist:
            return JsonResponse({"error": "Not Found"}, status=404)
    elif request.method == 'DELETE':
        try:
            image_record = Image.objects.get(id=image_id)
            file_key = image_record.url.split(f"{BUCKET_NAME}.s3.amazonaws.com/")[1]
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)
            image_record.delete()
            return JsonResponse({}, status=204)
        except Image.DoesNotExist:
            return JsonResponse({"error": "Not Found"}, status=404)
    else:
        return JsonResponse({"error": "Method Not Allowed."}, status=405)