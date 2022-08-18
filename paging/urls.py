
from django.urls import path
from .views import  *

urlpatterns = [
    path('add_facebook_page',FacebookPagePublish.as_view(),name='FacebookPagePublish'),

]
