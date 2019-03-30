from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

from .events import views

urlpatterns = [
    url('^docs$', views.Docs.as_view(), name='docs'),
    url('^docs/validator$', views.Validator.as_view(), name='docs'),
    url('^log$', views.LogList.as_view(), name='logs'),
    url('^events$', views.EventList.as_view(), name='events'),
    # url('^events/calendar$', views.EventCalendar.as_view(), name='events'),
    url('^feed/new$', views.EventFeed.as_view(), name='feed.new'),
    url('^feed/updates$', views.EventFeed.as_view(), name='feed.updates'),
    url('^$', views.StartPage.as_view(), name='startpage'),
]
