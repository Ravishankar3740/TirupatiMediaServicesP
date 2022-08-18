
from django.urls import path
from .views import  *

urlpatterns = [
    path('add_facebook_page',FacebookPagePublish.as_view(),name='add_facebook_page'),
    path('',home_page,name='HomePage'),

]

