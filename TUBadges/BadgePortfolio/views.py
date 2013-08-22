from django.contrib.auth.models import Permission
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from BadgePortfolio.models import *
from login_handler import check_if_login
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


def badges(request):
    """
    The Badges view.
    If an uid is given this view will list all public badges of the given User.
    If no uid is given this view will show all Badges of the logged in user.
    :type request: HttpRequest
    """
    check_if_login(request)
    if 'uid' in request.GET:
        content = { 'badges': Badge.objects.filter(awardee=request.GET['uid'], public=True) }
        content.update(get_header_content(request))

        return render_to_response(
            'badges.html',
            content
        )
    elif 'uID' in request.session:
        content = {'badges': Badge.objects.filter(awardee=request.session['uID'])}
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
    if request.user.is_authenticated() and request.user.has_perm(Permission.objects.get(codename='can_have_presets')):
        content = {'presets': BadgePreset.objects.filter(owner=request.user.id)}
        content.update(get_header_content(request))

        return render_to_response('presets.html', content)
    else:
        return login(request)


def get_header_content(request):
    content = {}

    if 'uID' in request.session:
        bu = BadgeUser.objects.get(id=request.session['uID'])
        content['username'] = bu.firstname+' '+bu.lastname
        if bu.role == BadgeUser.PROFESSOR:
            content['prof'] = True

    content['greeting'] = choice(['Willkommen', 'Hej', 'Oh Hai!', 'Servus', 'Hello', 'Bonjour', 'Salut', 'Nei Ho', 'Aloha', 'Ciao', 'Hola', 'Kon-nichiwa', 'Namaste'])

    return content