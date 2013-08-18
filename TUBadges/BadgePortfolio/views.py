from django.contrib.auth.models import Permission
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from BadgePortfolio.models import *


def index(request):
    """
    The index or home view. Forwards the request to the badges View.
    """
    if request.user.is_authenticated():
        return badges(request)
    else:
        return login(request)


def login(request):
    """
    The login view.
    """
    return render_to_response('login.html')


def badges(request):
    """
    The Badges view.
    If an uid is given this view will list all public badges of the given User.
    If no uid is given this view will show all Badges of the logged in user.
    """

    if request.user.is_authenticated():
        return render_to_response('badges.html', {'badges': Badge.objects.filter(awardee=request.user.email)})
    else:
        return login(request)


def presets(request):
    """

    :param request:
    :return:
    """
    if request.user.is_authenticated() & request.user.has_perm(Permission.objects.get(codename='can_have_presets')):
        return render_to_response('presets.html', {'presets': BadgePreset.objects.filter(owner=request.user.id)})
    else:
        return login(request)