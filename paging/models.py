from django.db import models

# Create your models here.

class FacebookPages(models.Model):
    builder_name = models.CharField(max_length=30,null=False,blank=False)
    facebook_page = models.CharField(max_length=50,null=False,blank=False,unique=True)
    whats_app_number = models.CharField(max_length=10,null=False,blank=False)
    published_date = models.DateField(null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

