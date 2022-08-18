from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FacebookPagesSerializers
from .models import FacebookPages


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