# webapp/image_upload/urls.py
from django.urls import path
from .views import upload_image, handle_image

urlpatterns = [
    path('v1/file', upload_image, name='upload_image'),
    path('v1/file/<str:image_id>', handle_image, name='handle_image'),
]