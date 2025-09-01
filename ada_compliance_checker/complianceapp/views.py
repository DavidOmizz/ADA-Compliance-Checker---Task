from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HTMLCheckSerializer
from .utils import check_document
from django.http import HttpResponse




def check_view(request):
    return HttpResponse("Hello World")


class CheckHTMLView(APIView):
    def post(self, request):
        serializer = HTMLCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        html = serializer.validated_data['html']
        issues = check_document(html)
        return Response({'issues': issues}, status=status.HTTP_200_OK)