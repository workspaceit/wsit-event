"""wsitEvent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from app.views import mobile_device
from publicfront.views import event
# import os
# from django.conf import settings

urlpatterns = [
    url(r'^retrieve-password/', event.RetrivePasswrod.as_view(), name='retrieve-password'),
    url(r'^send-retrive-passwrod-mail-by-eventid/', event.RetrivePasswrod.sendRetrivePasswrodMailByID, name='send-retrive-passwrod-mail-by-eventid'),
    url(r'^health/', event.RootEvent.health, name='health'),
    url(r'^admin/', include('app.urls')),
    url(r'^$', event.RootEvent.as_view(), name='home'),
    # url(r'^django-admin/', include(admin.site.urls)),
    # For mobile device services
    url(r'^device/token$', mobile_device.storeDeviceToken, name='device_token'),
    url(r'^device/message$', mobile_device.SendMessage, name='device_message'),
    url(r'^device/(?P<secret_key>[0-9a-zA-Z]+)/route$', mobile_device.getRouteUser, name='device_get_route'),
    url(r'^(?P<event_url>[\w-]+)/', include('publicfront.urls')),
]
# handler404 = event.RootEvent.page_not_found
# handler500 = event.RootEvent.server_error
# handler403 = event.RootEvent.permission_denied
# handler400 = event.RootEvent.bad_request

# if os.environ['ENVIRONMENT_TYPE'] == 'development':
#     if settings.DEBUG:
#         import debug_toolbar
#         urlpatterns = [
#             url(r'^__debug__/', include(debug_toolbar.urls)),
#         ] + urlpatterns

