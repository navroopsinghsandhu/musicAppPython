"""MusicAppBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from django.urls import re_path as url
from MusicAppBackend import views

urlpatterns = [
    path('admin/', admin.site.urls),

    url(r'^register$',views.userRegistrationApi),

    url(r'^login$',views.userLoginApi),

    # to get all the songs or filtered music for query
    url(r'^music$',views.allMusicApi),
    url(r'^music/([0-9]+)$',views.allMusicApi),

    # to get music each user subscribed to
    url(r'^musicuser$',views.userMusicMapApi),

    url(r'^subscribedmusicuser$',views.subscribedMusicApi)

    # url(r'^musicuser/([0-9]+)$',views.userMusicMapApi),
    # # to map a song to a user with userId, musicId
    # url(r'^musicuser/([0-9]+)/([0-9]+)$',views.userMusicMapApi) 
]
