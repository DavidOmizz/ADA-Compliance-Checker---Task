from django.urls import path
from .views import CheckHTMLView, check_view


urlpatterns = [
    path('check/', CheckHTMLView.as_view(), name='check-html'),
]