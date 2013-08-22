from django.contrib.auth.models import Permission
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from BadgePortfolio.models import *
from login_handler import check_if_login
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
        return render_to_response('badges.html', {'badges': Badge.objects.filter(awardee=request.GET['uid'], public=True)})
    elif 'uID' in request.session:
        return render_to_response('badges.html', {'badges': Badge.objects.filter(awardee=request.session['uID'])})
    else:
        return login(request)


def presets(request):
    """

    :param request:
    :return:
    """
    if request.user.is_authenticated() and request.user.has_perm(Permission.objects.get(codename='can_have_presets')):
        return render_to_response('presets.html', {'presets': BadgePreset.objects.filter(owner=request.user.id)})
    else:
        return login(request)