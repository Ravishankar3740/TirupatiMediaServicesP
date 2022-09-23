import json
from django.shortcuts import render,redirect
from .serializers import FacebookPagesSerializers,FacebookLeadDataDumpingSerializers
from .models import FacebookPages,FacebookLeadDataDumping
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import requests
import os
from pathlib import Path
import openpyxl
from django.contrib.auth import authenticate
from django.contrib.auth import logout


BASE_DIR = Path(__file__).resolve().parent.parent
pdfpath = os.path.join(BASE_DIR, 'media')

def FacebookPagePublish(request):
    """In this api we are performing the crud operation for facebook page published"""
    if request.method == "GET":
        return render(request, 'paging/Home.html')

    else:
        serializer = FacebookPagesSerializers(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            numbers = {}
            if len(request.POST) > 5:
                for i in list(request.POST.keys()):
                    if i.startswith('whats_app_no'):
                        numbers[i] = request.POST.get(i)
                FacebookPages.objects.filter(id=serializer.data.get('id')).update(multiplewhatsappno=numbers)
            return render(request, 'paging/lead_send.html', {
                "messages": [{"text": "facebook page successfully added", "icon": "success", "title": "Good job!"}]})
        return render(request, 'paging/Home.html',
                      {"messages": [{"text": "Facebook Page Already Exists", "icon": "error", "title": "Bad job!"}]})



def home_page(request):
    if request.method == "GET":
        return render(request, 'paging/Home.html')


def FacebookLeadDump(request):
    """ In this we are writing logic for dumping code into database"""
    if request.method == "GET":
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request,'paging/import_leads.html',{'page_name_list':page_name_list.data})

    else:
        lead_data = request.FILES['file']
        ad_name = request.POST.get('ad_name')
        page_name = FacebookPages.objects.get(facebook_page=ad_name)
        df = pd.read_excel(lead_data, engine='openpyxl')
        df['facebook_page'] = page_name.id
        df['created_time'] = pd.to_datetime(df['created_time']).dt.strftime('%Y-%m-%d')
        if 'in_which_property_are_you_interested_?' in list(df.columns):
            df.rename(columns={'in_which_property_are_you_interested_?': 'interested'}, inplace=True)
        df.rename(columns={'id': 'lead_id'}, inplace=True)
        df_json = df.to_json(orient='records')
        for i in json.loads(df_json):
            if not FacebookLeadDataDumping.objects.filter(lead_id=i['lead_id']).exists():
                serializer = FacebookLeadDataDumpingSerializers(data=i)
                if serializer.is_valid():
                    serializer.save()
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/lead_send.html', {"page_name_list": page_name_list.data,
                                                         "messages": [{"text": "All leads has been added successfully",
                                                                       "icon": "success", "title": "Good job!"}]})


def SendWhatsAPPleadToBuilder(request):
    """ In this class we are sending leads to builder """
    if request.method == "GET":
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/lead_send.html', {'page_name_list': page_name_list.data})

    else:
        ad_name = request.POST.get('ad_name')
        faacebook_page = FacebookPages.objects.get(facebook_page=ad_name)
        lead_data = FacebookLeadDataDumping.objects.filter(facebook_page=faacebook_page,is_lead_sent=False)
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        if lead_data:
            ad_lead_data = FacebookLeadDataDumpingSerializers(lead_data,many=True).data
            url = "https://betablaster.in/api/send.php"
            message = 'Facebook & Instagram Sponsor Ad Leads from TIRUPATI MEDIA SERVICESS...\n\n\n'
            for data in range(len(ad_lead_data)):
                message = message + ad_lead_data[data].get('full_name')+'\n'+ ad_lead_data[data].get('phone_number')+'\n'+ ad_lead_data[data].get('email')+'\n'+ad_lead_data[data].get('city')+'\n'+'-------------------------------'
                message += '\n'
            if not faacebook_page.multiplewhatsappno:
                params = {"number": "91" + faacebook_page.whats_app_number, "type": "text", "message": message,
                          "instance_id": "632C22898C690", "access_token": "099cc469861f811b7e139cf8b9cc2565"}
                data = requests.post(url, params=params, verify=False)
            else:
                d = list(faacebook_page.multiplewhatsappno.values())
                for i in d:
                    params = {"number": "91" + i, "type": "text", "message": message,
                              "instance_id": "632C22898C690", "access_token": "099cc469861f811b7e139cf8b9cc2565"}
                    data = requests.post(url, params=params, verify=False)
            lead_data.update(is_lead_sent=True)
            return render(request, 'paging/sendpdf.html', {"page_name_list": page_name_list.data,
                                                             "messages": [
                                                                 {"text": "All leads has been send to your concern person",
                                                                  "icon": "success", "title": "Good job!"}]})
        return render(request, 'paging/lead_send.html',
                      {"page_name_list": page_name_list.data,"messages": [{"text": "No leads are pending for this Ad page", "icon": "error", "title": "Not New Leads!"}]})

def SendleadInPdf(request):
    if request.method == "GET":
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/sendpdf.html', {'page_name_list': page_name_list.data})
    else:
        startdate = request.POST.get('startdate')
        enddate =  request.POST.get('enddate')
        ad_name = request.POST.get('ad_name')
        faacebook_page = FacebookPages.objects.get(facebook_page=ad_name)
        lead_data = FacebookLeadDataDumping.objects.filter(facebook_page=faacebook_page, created_time__range=[startdate,enddate]).values('interested','full_name','phone_number','email','city')
        if lead_data:
            if lead_data[0]['interested']:
                col = ('interested', 'full_name', 'phone_number', 'email', 'city')
            else:
                col = ('full_name', 'phone_number', 'email', 'city')
            df = pd.DataFrame(lead_data, columns=col)
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.axis('tight')
            ax.axis('off')
            ax.table(cellText=df.values, colLabels=df.columns, loc='center')
            ax.set_title('Facebook & Instagram Sponsor Ad Leads from TIRUPATI MEDIA SERVICESS',y=1.20)
            pp = PdfPages("//home//othersitesdata//leadapp.gruhkhoj.in//public//media//" +"//"+ad_name+".pdf")
            pp.savefig(fig, bbox_inches='tight')
            pp.close()
            faacebook_page = FacebookPages.objects.get(facebook_page=ad_name)
            url = "https://betablaster.in/api/send.php"
            params = {"number": "91" + faacebook_page.whats_app_number, "type": "media", "filename":ad_name+".pdf","message":"Facebook & Instagram Sponsor Ad Leads from TIRUPATI MEDIA SERVICESS","media_url": "http://www.leadapp.gruhkhoj.in/media/"+ad_name+".pdf",
                      "instance_id": "632C22898C690", "access_token": "099cc469861f811b7e139cf8b9cc2565"}
            data = requests.post(url, params=params, verify=False)
            if request.POST.get('getown'):
                params = {"number": "91" +"9325201010", "type": "media", "filename": ad_name+".pdf",
                          "message": "Facebook & Instagram Sponsor Ad Leads from TIRUPATI MEDIA SERVICESS", "media_url": "http://www.leadapp.gruhkhoj.in/media/"+ad_name+".pdf",
                          "instance_id": "632C22898C690", "access_token": "099cc469861f811b7e139cf8b9cc2565"}
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


def LoginView(request):
    if request.method == "GET":
        return render(request,'paging/login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            return redirect('HomePage')

        else:
            return render(request, 'paging/login.html', {"messages": [
                                                               {"text": "Invalid Credentials",
                                                                "icon": "error", "title": "User Not Found!"}]})

def LogoutView(request):
    if request.method == "GET":
        logout(request)
        return render(request, 'paging/login.html')


