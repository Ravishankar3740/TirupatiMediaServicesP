
from django.urls import path
from .views import  *

urlpatterns = [
    path('add_facebook_page',FacebookPagePublish.as_view(),name='add_facebook_page'),
    path('dump_facebook_lead_data',FacebookLeadDump.as_view(),name="dump_facebook_lead_data"),
    path("send_whats_app_lead",SendWhatsAPPleadToBuilder.as_view(),name="send_whats_app_lead"),
    path("send_pdf_lead",SendleadInPdf.as_view(),name="send_pdf_lead"),
    path('HomePage/',home_page,name='HomePage'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('',LoginView.as_view(),name="login")


]

