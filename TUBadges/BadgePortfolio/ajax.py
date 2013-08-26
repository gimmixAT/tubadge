from django.contrib.auth.models import Permission
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from BadgePortfolio.models import *
from login_handler import *
from random import choice
from django.core.serializers import serialize
import logging


def issue_badge_form(request):
    """
    Returns the HTML for the badge issuing form
    :type request: HttpRequest
    """
    if is_logged_in(request):
        content = {}
        bu = get_loggedin_user(request)
        if bu.role is BadgeUser.PROFESSOR:
            if 'pid' in request.GET and request.GET['pid'] != '' and BadgePreset.objects.exists(id=request.GET['pid']):
                bp = BadgePreset.objects.get(id=request.GET['pid'])
                content.update({
                    'name': bp.name,
                    'img': bp.img,
                    'keywords': bp.keywords,
                    'issuer': bu.firstname+' '+bu.lastname,
                    'issuer_id': bu.id
                })
            return render_to_response('badge_form.html', content)
        else:
            return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
    else:
        return render_to_response('error.html', {'msg': 'Sie m&uuml;ssen eingeloggt sein.'})


def badge_preset_form(request):
    """
    Returns the HTML for the badge preset form
    :type request: HttpRequest
    """
    if is_logged_in(request):
        content = {}
        bu = get_loggedin_user(request)
        if bu.role is BadgeUser.PROFESSOR:
            if 'pid' in request.GET and request.GET['pid'] != '' and BadgePreset.objects.exists(id=request.GET['pid']):
                bp = BadgePreset.objects.get(id=request.GET['pid'])
                content.update({
                    'name': bp.name,
                    'img': bp.img,
                    'keywords': bp.keywords
                })
            return render_to_response('badge_preset_form.html', content)
        else:
            return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
    else:
        return render_to_response('error.html', {'msg': 'Sie m&uuml;ssen eingeloggt sein.'})


def issue_badge(request):
    """
    Issues the requested badge and returns a JSON response
    :type request: HttpRequest
    """
    result = {}
    #check if a user id is given
        #if no user id is given check if the name is a studentID and create a new user
    return HttpResponse(serialize('json', result), content_type="application/json")


def save_badge_preset(request):
    """
    Saves the requested badge preset and returns a JSON response
    :type request: HttpRequest
    """
    result = {}
    return HttpResponse(serialize('json', result), content_type="application/json")


def toggle_public(request):
    """
    Toggles the public state of the requested badge and returns a JSON response
    :type request: HttpRequest
    """
    if is_logged_in(request):
        if 'bid' in request.GET and request.GET['bid'] != '' and Badge.objects.exists(id=request.GET['bid']):
            badge = Badge.objects.get(id=request.GET['bid'])
            if badge.awardee.id == request.session['uID']:
                badge.public = not badge.public
                badge.save()
                result = {'error': False, 'msg': 'Erfolgreich gespeichert.', 'public': badge.public}
            else:
                result = {'error': True, 'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'}
        else:
            result = {'error': True, 'msg': 'Es fehlt die BadgeID oder diese ist nicht g&uuml;ltig.'}
    else:
        result = {'error': True, 'msg': 'Sie m&uuml;ssen eingeloggt sein.'}
    return HttpResponse(serialize('json', result), content_type="application/json")


def get_user(request):
    """
    Tries to find a matching user and returns the ID as JSON
    :type request: HttpRequest
    """
    if is_logged_in(request):
        if 's' in request.GET and request.GET['s'] != '':
            if get_loggedin_user(request).role is BadgeUser.PROFESSOR:
                u = BadgeUser.get_matching_user(request.GET['s'])
                if u is not None:
                    result = {'error': False, 'msg': 'User gefunden.', 'uid': u.id}
                else:
                    result = {'error': True, 'msg': 'Kein User gefunden.'}
            else:
                result = {'error': True, 'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'}
        else:
            result = {'error':True, 'msg':'Es fehlt ein Suchparameter.'}
    else:
        result = {'error': True, 'msg': 'Sie m&uuml;ssen eingeloggt sein.'}

    return HttpResponse(serialize('json', result), content_type="application/json")