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
import re


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
                if bp.issued_badges.count() is 0:
                    content.update({
                        'name': bp.name,
                        'img': bp.img,
                        'keywords': bp.keywords
                    })
                    return render_to_response('badge_preset_form.html', content)
                else:
                    return render_to_response('error.html', {'msg': 'Das Badge Preset wurde bereits verwendet und kann nicht mehr editiert werden.'})
            else:
                return render_to_response('error.html', {'msg': 'Das Badge Preset existiert nicht.'})
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
    awardee = None
    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role is BadgeUser.PROFESSOR:
            if 'awardee_id' in request.GET:
                #if a user id is given
                awardee = BadgeUser.objects.get(id=request.GET['awardee_id'])
            elif 'awardee' in request.GET:
                # if no user id is given check if the name is a studentID and
                # create a new user if the studentID isn't already in use
                if re.match('^[0-9]{7}$', request.GET['awardee'], re.IGNORECASE):
                    if BadgeUser.objects.exists(studentID=request.GET['awardee']):
                        awardee = BadgeUser.objects.get(studentID=request.GET['awardee'])

                    if awardee is None:
                        awardee = BadgeUser()
                        awardee.student_id = request.GET['awardee']
                        awardee.save()
                else:
                    result = {
                        'error': True,
                        'msg': 'Ung&uuml;tiger Badge empf&auml;nger.'
                    }
            else:
                result = {
                    'error': True,
                    'msg': 'Es fehlt ein Parameter'
                }

            if awardee is not None:
                #issue badge
                b = None
                if 'pid' in request.GET and BadgePreset.objects.exists(id=request.GET['pid']):
                    bp = BadgePreset.objects.get(id=request.GET['pid'])
                    if bp.owner is bu.id:
                        b = Badge()
                        b.name = bp.name
                        b.keywords = bp.keywords
                        b.img = bp.img
                        b.preset = bp
                    else:
                        result = {
                            'error': True,
                            'msg': 'Sie haben nicht die n&ouml;tigen Rechte um dieses Badge Preset zu verwenden.'
                        }
                elif 'name' in request.GET and 'img' in request.GET:
                    b = Badge()
                    b.name = request.GET['name']
                    b.img = request.GET['img']
                else:
                    result = {
                        'error': True,
                        'msg': 'Es fehlt ein Parameter'
                    }

                if b is not None:
#TODO: sanity checking GET
                    if 'keywords' in request.GET:
                        b.keywords += request.GET['keywords']

                    b.awardee = awardee

                    if 'awarder' in request.GET:
                        b.awarder = request.GET['awarder']
                    else:
                        b.awarder = bu.id

                    b.rating = request.GET['rating']
                    b.issuer = bu
                    b.candidates = request.GET['candidates']
                    b.proof_url = request.GET['proof']

#TODO: store LVA information if necessary

                    b.lva = request.GET['lva']

                    b.save()

                    result = {
                        'error': False,
                        'id': b.id
                    }
        else:
            result = {
                'error': True,
                'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'
            }
    else:
        result = {
            'error': True,
            'msg': 'Sie m&uuml;ssen eingeloggt sein.'
        }

    return HttpResponse(serialize('json', result), content_type="application/json")


def save_badge_preset(request):
    """
    Saves the requested badge preset and returns a JSON response
    :type request: HttpRequest
    """
    result = {'error': True, 'msg': ''}

    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role is BadgeUser.PROFESSOR:
            bp = None
            if 'pid' in request.GET and request.GET['pid'] != '':
                if BadgePreset.objects.exists(id=request.GET['pid']):
                    bp = BadgePreset.objects.get(id=request.GET['pid'])
                    if bp.owner.id is not get_loggedin_user().id:
                        bp = None
                        result = {
                            'error': True,
                            'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'
                        }
                else:
                    result = {
                        'error': True,
                        'msg': 'Badge Preset existiert nicht.'
                    }
            else:
                bp = BadgePreset()
                bp.owner = get_loggedin_user()

            if bp is not None:
                if bp.issued_badges.count() is 0:
                    if 'name' in request.GET:
                        bp.name = request.GET['name']
                    if 'img' in request.GET:
                        bp.img = request.GET['img']
                    if 'keywords' in request.GET:
                        bp.keywords = request.GET['keywords']

                    bp.save()
                    result = {
                        'error': False,
                        'id': bp.id
                    }
                else:
                    result = {
                        'error': True,
                        'msg': 'Das Badge Preset wurde bereits verwendet und kann nicht mehr editiert werden.',
                        'id': bp.id
                    }
        else:
            result = {
                'error': True,
                'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'
            }
    else:
        result = {
            'error': True,
            'msg': 'Sie m&uuml;ssen eingeloggt sein.'
        }

    return HttpResponse(serialize('json', result), content_type="application/json")


def duplicate_badge_preset(request):
    """
    Tries to duplicate the requested badge preset and returns a JSON response
    :type request: HttpRequest
    """
    result = {'error': True, 'msg': ''}

    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role is BadgeUser.PROFESSOR:
            if 'pid' in request.GET and request.GET['pid'] != '' and BadgePreset.objects.exists(id=request.GET['pid']):
                bp = BadgePreset.objects.get(id=request.GET['pid'])
                if bp.owner.id is get_loggedin_user().id:
                    bpn = BadgePreset()
                    bpn.name = bp.name + "*"
                    bpn.img = bp.img
                    bpn.keywords = bp.keywords
                    bpn.owner = bp.owner
                    bpn.save()

                    result = {
                        'error': False,
                        'id': bpn.id
                    }
                else:
                    result = {
                        'error': True,
                        'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'
                    }
            else:
                result = {
                    'error': True,
                    'msg': 'Badge Preset existiert nicht.'
                }
        else:
            result = {
                'error': True,
                'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'
            }
    else:
        result = {
            'error': True,
            'msg': 'Sie m&uuml;ssen eingeloggt sein.'
        }

    return HttpResponse(serialize('json', result), content_type="application/json")


def toggle_public(request):
    """
    Toggles the public state of the requested badge and returns a JSON response
    :type request: HttpRequest
    """
    if is_logged_in(request):
        if 'bid' in request.GET and request.GET['bid'] != '' and Badge.objects.exists(id=request.GET['bid']):
            badge = Badge.objects.get(id=request.GET['bid'])
            if badge.awardee.id == get_loggedin_user().id:
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


def get_courses(request):
    """
    Tries to find matching courses and returns the resulting list as JSON
    :type request: HttpRequest
    """
    result = {}
    if 'q' in request.GET:
        q = request.GET['q']
        courses = []
        qm = re.match('^([0-9]{3})\.([0-9]{0,3})$', q);
        if qm:
            #tries to find a course by institute and course id
            for co in LVA.objects.filter(institute=qm.group(0), number=qm.group(1)):
                courses.append({
                    'id': co.id,
                    'title': co.institute+"."+co.number+" "+co.title,
                    'students': co.students
                })
        elif re.match('^[0-9]{3}$', q):
            #tries to find courses by courseid
            for co in LVA.objects.filter(number=q):
                courses.append({
                    'id': co.id,
                    'title': co.institute+"."+co.number+" "+co.title,
                    'students': co.students
                })
        else:
            #trues to find a course by mathing the title
            for co in LVA.objects.filter(title__icontains=q):
                courses.append({
                    'id': co.id,
                    'title': co.institute+"."+co.number+" "+co.title,
                    'students': co.students
                })
        result = {'error': False, 'courses': courses}
    else:
        result = {'error': True, 'msg': 'Es fehlt ein Parameter.', 'courses': []}

    return HttpResponse(serialize('json', result), content_type="application/json")
