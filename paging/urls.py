
from django.urls import path
from .views import  *

urlpatterns = [
    path('add_facebook_page',FacebookPagePublish.as_view(),name='add_facebook_page'),
    path('dump_facebook_lead_data',FacebookLeadDump.as_view(),name="dump_facebook_lead_data"),
    path('',home_page,name='HomePage'),

]

