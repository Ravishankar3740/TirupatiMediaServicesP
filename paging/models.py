from django.db import models
import jsonfield

# Create your models here.

class FacebookPages(models.Model):
    builder_name = models.CharField(max_length=30,null=False,blank=False)
    facebook_page = models.CharField(max_length=50,null=False,blank=False,unique=True)
    whats_app_number = models.CharField(max_length=10,null=False,blank=False)
    published_date = models.DateField(null=False,blank=False)
    multiplewhatsappno = jsonfield.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class FacebookLeadDataDumping(models.Model):
    facebook_page = models.ForeignKey('FacebookPages',on_delete=models.CASCADE)
    lead_id =  models.CharField(max_length=100,null=False,blank=False)
    ad_name = models.CharField(max_length=30,null=False,blank=False)
    full_name = models.CharField(max_length=50,null=False,blank=False)
    phone_number = models.CharField(max_length=13,null=False,blank=False)
    email = models.CharField(max_length=50,null=False,blank=False)
    created_time = models.DateField(null=False,blank=False)
    city = models.CharField(max_length=50,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    interested = models.CharField(max_length=20,null=True,blank=True)
    is_lead_sent = models.BooleanField(default=False,null=True,blank=True)



