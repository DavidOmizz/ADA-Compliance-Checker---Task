from rest_framework import serializers


class HTMLCheckSerializer(serializers.Serializer):
    html = serializers.CharField()