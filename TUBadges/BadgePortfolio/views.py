from django.contrib.auth.models import Permission
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from BadgePortfolio.models import *
from login_handler import *
from random import choice

import logging

logger = logging.getLogger(__name__)


def login(request):
    """
    The login view.
    """
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)


def badges(request, uid=None):
    """
    The Badges view.
    If an uid is given this view will list all public badges of the given User.
    If no uid is given this view will show all Badges of the logged in user.
    :type request: HttpRequest
    """
    loginresponse = check_if_login(request)
    if loginresponse: return loginresponse

    if 'uid' in request.GET:
        uid = request.GET['uid']

    if uid and BadgeUser.objects.filter(id=uid).exists():
        bu = BadgeUser.objects.get(id=uid)
        content = {
            'badges': Badge.objects.filter(awardee=uid, public=True),
            'public': True,
            'title': bu.firstname+' '+bu.lastname+'s Badges',
            'page': bu.firstname+' '+bu.lastname+'s Badges'
        }
        content.update(get_header_content(request))

        return render_to_response(
            'badges.html',
            content
        )
    elif is_logged_in(request):
        content = {
            'badges': Badge.objects.filter(awardee=request.session['uID']),
            'page': 'Meine Badges',
            'title': 'Meine Badges'
        }
        content.update(get_header_content(request))

        return render_to_response(
            'badges.html',
            content
        )
    else:
        return login(request)


def presets(request):
    """

    :param request:
    :return:
    """
    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            content = {'presets': BadgePreset.objects.filter(owner=bu.id)}
            content.update(get_header_content(request))

            return render_to_response('presets.html', content)
        else:
            return badges(request)
    else:
        return login(request)


def get_header_content(request):
    content = {}

    if 'uID' in request.session:
        bu = get_loggedin_user(request)
        content['username'] = bu.firstname+' '+bu.lastname
        if bu.role == BadgeUser.PROFESSOR:
            content['prof'] = True

    content['greeting'] = choice(['Willkommen', 'Hej', 'Oh Hai!', 'Servus', 'Hello', 'Bonjour', 'Salut', 'Nei Ho', 'Aloha', 'Ciao', 'Hola', 'Kon-nichiwa', 'Namaste'])

    return content