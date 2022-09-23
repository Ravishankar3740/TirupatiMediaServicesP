
from django.urls import path
from .views import  *

urlpatterns = [
    path('add_facebook_page',FacebookPagePublish,name='add_facebook_page'),
    path('dump_facebook_lead_data',FacebookLeadDump,name="dump_facebook_lead_data"),
    path("send_whats_app_lead",SendWhatsAPPleadToBuilder,name="send_whats_app_lead"),
    path("send_pdf_lead",SendleadInPdf,name="send_pdf_lead"),
    path('HomePage/',home_page,name='HomePage'),
    path('logout/', LogoutView, name='logout'),
    path('',LoginView,name="login")


]

