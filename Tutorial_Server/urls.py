"""tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include

from Tutorial import views

urlpatterns = [
    url(r'^hotel/find/$', views.HotelFind.as_view(), name="HotelFind"),
    url(r'^destination/updates/$', views.DestinationUpdates.as_view(), name="DestinationUpdates"),
    url(r'^destination/sync/$', views.DestinationSync.as_view(), name="DestinationSync"),
    url(r'^hotel/updates/$', views.HotelUpdates.as_view(), name="DestinationUpdates"),
    url(r'^hotel/sync/$', views.HotelSync.as_view(), name="HotelSync"),
]
