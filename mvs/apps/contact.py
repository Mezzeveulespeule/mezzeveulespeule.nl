import html

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.core.mail import send_mail
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mvs.models import Vrijwilliger
