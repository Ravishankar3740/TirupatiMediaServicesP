
from django.urls import path
from .views import  *

urlpatterns = [
    path('',FacebookPagePublish.as_view(),name='FacebookPagePublish'),

]
