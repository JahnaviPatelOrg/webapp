from django.urls import path
from .views import upload_image, get_image, delete_image

urlpatterns = [
    path('v1/file', upload_image, name='upload_image'),
    path('v1/file/<str:image_id>', get_image, name='get_image'),
    path('v1/file/<str:image_id>', delete_image, name='delete_image'),
]