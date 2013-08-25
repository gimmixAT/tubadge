from django.contrib.auth.models import Permission
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from BadgePortfolio.models import *
from login_handler import check_if_login
from random import choice
import logging


def issue_badge_form(request):
    """

    :type request: HttpRequest
    """


def badge_preset_form(request):
    """

    :type request: HttpRequest
    """


def issue_badge(request):
    """

    :type request: HttpRequest
    """


def save_badge_preset(request):
    """

    :type request: HttpRequest
    """


def toggle_public(request):
    """

    :type request: HttpRequest
    """