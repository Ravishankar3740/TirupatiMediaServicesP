import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FacebookPagesSerializers,FacebookLeadDataDumpingSerializers
from .models import FacebookPages,FacebookLeadDataDumping
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import requests
import os
from pathlib import Path
import openpyxl

BASE_DIR = Path(__file__).resolve().parent.parent
pdfpath = os.path.join(BASE_DIR, 'media')
class FacebookPagePublish(APIView):
    """In this api we are performing the crud operation for facebook page published"""

    def get(self, request, format=None):
        return render(request, 'paging/Home.html')


    def post(self, request, format=None):
            serializer = FacebookPagesSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                numbers = {}
                if len(request.POST) >5:
                    for i in list(request.POST.keys()):
                        if i.startswith('whats_app_no'):
                            numbers[i] = request.POST.get(i)
                    FacebookPages.objects.filter(id=serializer.data.get('id')).update(multiplewhatsappno=numbers)
                return render(request, 'paging/Home.html', {"messages": [{"text":"facebook page successfully added","icon":"success","title": "Good job!"}]})
            return render(request, 'paging/Home.html', {"messages": [{"text":"facebook page already exists","icon":"error","title": "Bad job!"}]})


def home_page(request):
    return render(request, 'paging/Home.html')


class FacebookLeadDump(APIView):
    """ In this we are writing logic for dumping code into database"""

    def get(self,request):
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request,'paging/import_leads.html',{'page_name_list':page_name_list.data})

    def post(self,request):
        lead_data = request.FILES['file']
        ad_name = request.data.get('ad_name')
        page_name = FacebookPages.objects.get(facebook_page=ad_name)
        df = pd.read_excel(lead_data,engine='openpyxl')
        df['facebook_page'] = page_name.id
        df['created_time'] = pd.to_datetime(df['created_time']).dt.strftime('%Y-%m-%d')
        df.rename(columns={'id': 'lead_id'},inplace = True)
        df_json = df.to_json(orient='records')
        for i in json.loads(df_json):
            if not FacebookLeadDataDumping.objects.filter(lead_id = i['lead_id']).exists():
                serializer = FacebookLeadDataDumpingSerializers(data=i)
                if serializer.is_valid():
                    serializer.save()
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/lead_send.html', {"page_name_list":page_name_list.data,
            "messages": [{"text": "All leads has been added successfully", "icon": "success", "title": "Good job!"}]})


class SendWhatsAPPleadToBuilder(APIView):
    """ In this class we are sending leads to builder """

    def get(self,request):
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/lead_send.html', {'page_name_list': page_name_list.data})

    def post(self,request):
        ad_name = request.data.get('ad_name')
        faacebook_page = FacebookPages.objects.get(facebook_page=ad_name)
        lead_data = FacebookLeadDataDumping.objects.filter(facebook_page=faacebook_page,is_lead_sent=False)
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        if lead_data:
            ad_lead_data = FacebookLeadDataDumpingSerializers(lead_data,many=True).data
            url = "https://betablaster.in/api/send.php"
            message = 'Facebook Leads....\n\n\n'
            for data in range(len(ad_lead_data)):
                message = message + ad_lead_data[data].get('full_name')+'\n'+ ad_lead_data[data].get('phone_number')+'\n'+ ad_lead_data[data].get('email')+'\n'+ad_lead_data[data].get('city')+'\n'+'-------------------------------'
                message += '\n'
            print("test")
            if not faacebook_page.multiplewhatsappno:
                params = {"number": "91" + faacebook_page.whats_app_number, "type": "text", "message": message,
                          "instance_id": "6329BF36277A7", "access_token": "88b2435f1513c443ca80703de1b67943"}
                data = requests.post(url, params=params, verify=False)
            else:
                d = list(faacebook_page.multiplewhatsappno.values())
                for i in d:
                    params = {"number": "91" + i, "type": "text", "message": message,
                              "instance_id": "6329BF36277A7", "access_token": "88b2435f1513c443ca80703de1b67943"}
                    data = requests.post(url, params=params, verify=False)
            lead_data.update(is_lead_sent=True)
            return render(request, 'paging/lead_send.html', {"page_name_list": page_name_list.data,
                                                             "messages": [
                                                                 {"text": "All leads has been send to your concern person",
                                                                  "icon": "success", "title": "Good job!"}]})
        return render(request, 'paging/lead_send.html',
                      {"page_name_list": page_name_list.data,"messages": [{"text": "No leads are pending for this Ad page", "icon": "error", "title": "Not New Leads!"}]})

class SendleadInPdf(APIView):
    def get(self,request):
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/sendpdf.html', {'page_name_list': page_name_list.data})

    def post(self, request):
        startdate = request.POST.get('startdate')
        enddate =  request.POST.get('enddate')
        ad_name = request.POST.get('ad_name')
        faacebook_page = FacebookPages.objects.get(facebook_page=ad_name)
        lead_data = FacebookLeadDataDumping.objects.filter(facebook_page=faacebook_page, created_time__range=[startdate,enddate]).values('ad_name','full_name','phone_number','email','city')
        if lead_data:
            df = pd.DataFrame(lead_data, columns=('ad_name','full_name','phone_number','email','city'))
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.axis('tight')
            ax.axis('off')
            the_table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
            pp = PdfPages(pdfpath +"//"+ad_name+".pdf")
            pp.savefig(fig, bbox_inches='tight')
            pp.close()
            faacebook_page = FacebookPages.objects.get(facebook_page=ad_name)
            url = "https://betablaster.in/api/send.php"
            params = {"number": "91" + "9069505151", "type": "media", "filename":"sample.pdf","message":"Send by python for testing","media_url": "https://pythonists.pythonanywhere.com/media/"+ad_name+".pdf",
                      "instance_id": "6329BF36277A7", "access_token": "88b2435f1513c443ca80703de1b67943"}
            data = requests.post(url, params=params, verify=False)
            if request.POST.get('getown'):
                params = {"number": "91" +"9069505151", "type": "media", "filename": ad_name+".pdf",
                          "message": "Send by python for testing", "media_url": "https://pythonists.pythonanywhere.com/media/"+ad_name+".pdf",
                          "instance_id": "6329BF36277A7", "access_token": "88b2435f1513c443ca80703de1b67943"}
                data = requests.post(url, params=params, verify=False)
            page_names = FacebookPages.objects.all()
            page_name_list = FacebookPagesSerializers(page_names, many=True)

            return render(request, 'paging/sendpdf.html', {"page_name_list": page_name_list.data,
                                                             "messages": [
                                                                 {"text": "Attachment Successfully send",
                                                                  "icon": "success", "title": "Good job!"}]})
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/sendpdf.html', {"page_name_list": page_name_list.data,
                                                       "messages": [
                                                           {"text": "No data found in given range",
                                                            "icon": "error", "title": "Data Not Found!"}]})