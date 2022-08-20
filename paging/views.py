import json

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FacebookPagesSerializers,FacebookLeadDataDumpingSerializers
from .models import FacebookPages,FacebookLeadDataDumping
import pandas as pd


class FacebookPagePublish(APIView):
    """In this api we are performing the crud operation for facebook page published"""

    def get(self, request, format=None):
        snippets = FacebookPages.objects.all()
        serializer = FacebookPagesSerializers(snippets, many=True)
        return Response(serializer.data)


    def post(self, request, format=None):
            serializer = FacebookPagesSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        df = pd.read_csv(lead_data)
        df['facebook_page'] = page_name.id
        df['created_time'] = pd.to_datetime(df['created_time']).dt.strftime('%Y-%m-%d')
        df.rename(columns={'id': 'lead_id'},inplace = True)
        df_json = df.to_json(orient='records')
        for i in json.loads(df_json):
            if not FacebookLeadDataDumping.objects.filter(lead_id = i['lead_id']).exists():
                serializer = FacebookLeadDataDumpingSerializers(data=i)
                if serializer.is_valid():
                    serializer.save()
        return Response(status=status.HTTP_201_CREATED)

class SendWhatsAPPleadToBuilder(APIView):
    """ In this class we are sending leads to builder """

    def get(self,request):
        page_names = FacebookPages.objects.all()
        page_name_list = FacebookPagesSerializers(page_names, many=True)
        return render(request, 'paging/import_leads.html', {'page_name_list': page_name_list.data})

    def post(self,request):
        ad_name = request.data.get('ad_name')
        faacebook_page = FacebookPages.objects.get(facebook_page=ad_name)
        lead_data = FacebookLeadDataDumping.objects.filter(facebook_page=faacebook_page,is_lead_sent=False)
        if lead_data:
            ad_lead_data = FacebookLeadDataDumpingSerializers(lead_data,many=True).data
            url = "https://betablaster.in/api/send.php"
            import requests
            message = 'Facebook Leads....\n\n\n'
            for data in range(len(ad_lead_data)):
                message = message + ad_lead_data[data].get('full_name')+'\n'+ ad_lead_data[data].get('phone_number')+'\n'+ ad_lead_data[data].get('email')+'\n'+ad_lead_data[data].get('city')+'\n'+'-------------------------------'
                message += '\n'
            params = {"number": "919175346601", "type": "text", "message": message,
                      "instance_id": "630145B8D7452", "access_token": "fb1d7b8975b8a4a369bd0cedfa26c402"}
            data = requests.post(url, params=params, verify=False)
            lead_data.update(is_lead_sent=True)
            return Response(data.text, status=status.HTTP_201_CREATED)
        return Response({"notsent":"msg"})

