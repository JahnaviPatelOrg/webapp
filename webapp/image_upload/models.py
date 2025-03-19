from django.db import models
import uuid


# Create your models here.
class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    upload_date = models.DateField(auto_now_add=True,null=False)
    url = models.URLField(max_length=200)
    file_name = models.CharField(max_length=200)
