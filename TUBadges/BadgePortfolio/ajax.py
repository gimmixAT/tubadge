from django.contrib.auth.models import Permission
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from BadgePortfolio.models import *
from login_handler import *
from random import choice
import json
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
        if bu.role == BadgeUser.PROFESSOR:
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
        if bu.role == BadgeUser.PROFESSOR:
            if 'pid' in request.GET and request.GET['pid'] != '' and BadgePreset.objects.exists(id=request.GET['pid']):
                bp = BadgePreset.objects.get(id=request.GET['pid'])
                if bp.issued_badges.count() == 0:
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
    :param request:
    :type request: HttpRequest
    """
    result = {}
    awardee = None
    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            if 'awardee_id' in request.POST:
                #if a user id is given
                awardee = BadgeUser.objects.get(id=request.POST['awardee_id'])
            elif 'awardee' in request.POST:
                # if no user id is given check if the name is a studentID and
                # create a new user if the studentID isn't already in use
                if re.match('^[0-9]{7}$', request.POST['awardee'], re.IGNORECASE):
                    if BadgeUser.objects.exists(studentID=request.POST['awardee']):
                        awardee = BadgeUser.objects.get(studentID=request.POST['awardee'])

                    if not awardee:
                        awardee = BadgeUser()
                        awardee.student_id = request.POST['awardee']
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

            if awardee:
                #issue badge
                b = None
                if 'pid' in request.POST and BadgePreset.objects.exists(id=request.POST['pid']):
                    bp = BadgePreset.objects.get(id=request.POST['pid'])
                    if bp.owner == bu.id:
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
                elif 'name' in request.POST and 'img' in request.POST:
                    b = Badge()
                    b.name = request.POST['name']
                    b.img = request.POST['img']
                else:
                    result = {
                        'error': True,
                        'msg': 'Es fehlt ein Parameter'
                    }

                if b and 'rating' in request.POST and request.POST['rating'] >= 0 and request.POST['rating'] <= 3:
#TODO: sanity checking POST
                    if 'keywords' in request.POST:
                        b.keywords += request.POST['keywords']

                    b.awardee = awardee

                    if 'awarder' in request.POST and request.POST['awarder'] != '':
                        b.awarder = request.POST['awarder']
                    else:
                        b.awarder = bu.id


                    b.rating = request.POST['rating']
                    b.issuer = bu

                    if 'students' in request.POST:
                        b.candidates = request.POST['students']
                    else:
                        b.candidates = 1

                    b.proof_url = request.POST['proof']

                    if 'lva_id' not in request.POST or request.POST['lva_id'] == '':
                        if 'lva_title' in request.POST and request.POST['lva_title'] != '':
                            lva = LVA()
                            lva.title = request.POST['lva_title']
                            lva.institute = request.POST['lva_institute']
                            lva.number = request.POST['lva_number']
                            lva.students = request.POST['students']
                            lva.save()
                            b.lva = lva
                    else:
                        b.lva = LVA.objects.get(id=request.POST['lva_id'])

                    b.save()

                    result = {
                        'error': False,
                        'id': b.id
                    }
                else:
                    result = {
                        'error': True,
                        'msg': 'Es fehlt ein oder mehrere Parameter.'
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

    return HttpResponse(json.dumps(result), content_type="application/json")


def save_badge_preset(request):
    """
    Saves the requested badge preset and returns a JSON response
    :type request: HttpRequest
    """
    result = {'error': True, 'msg': ''}

    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            bp = None
            if 'pid' in request.POST and request.POST['pid'] != '':
                if BadgePreset.objects.exists(id=request.POST['pid']):
                    bp = BadgePreset.objects.get(id=request.POST['pid'])
                    if bp.owner.id != get_loggedin_user().id:
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

            if bp:
                if bp.issued_badges.count() == 0:
                    if 'name' in request.POST:
                        bp.name = request.POST['name']
                    if 'img' in request.POST:
                        bp.img = request.POST['img']
                    if 'keywords' in request.POST:
                        bp.keywords = request.POST['keywords']

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

    return HttpResponse(json.dumps(result), content_type="application/json")


def duplicate_badge_preset(request):
    """
    Tries to duplicate the requested badge preset and returns a JSON response
    :type request: HttpRequest
    """
    result = {'error': True, 'msg': ''}

    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            if 'pid' in request.POST and request.POST['pid'] != '' and BadgePreset.objects.exists(id=request.POST['pid']):
                bp = BadgePreset.objects.get(id=request.POST['pid'])
                if bp.owner.id == get_loggedin_user().id:
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

    return HttpResponse(json.dumps(result), content_type="application/json")


def toggle_public(request):
    """
    Toggles the public state of the requested badge and returns a JSON response
    :type request: HttpRequest
    """
    if is_logged_in(request):
        if 'bid' in request.POST and request.POST['bid'] != '' and Badge.objects.exists(id=request.POST['bid']):
            badge = Badge.objects.get(id=request.POST['bid'])
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
    return HttpResponse(json.dumps(result), content_type="application/json")


def get_user(request):
    """
    Tries to find a matching user and returns the ID as JSON
    :type request: HttpRequest
    """
    if is_logged_in(request):
        if 'q' in request.GET and request.GET['q'] != '':
            if get_loggedin_user(request).role == BadgeUser.PROFESSOR:
                u = BadgeUser.get_matching_user(request.GET['q'])
                if u:
                    result = {'error': False, 'msg': 'User gefunden.', 'uid': u.id}
                else:
                    result = {'error': True, 'msg': 'Kein User gefunden.'}
            else:
                result = {'error': True, 'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'}
        else:
            result = {'error':True, 'msg':'Es fehlt ein Suchparameter.'}
    else:
        result = {'error': True, 'msg': 'Sie m&uuml;ssen eingeloggt sein.'}

    return HttpResponse(json.dumps(result), content_type="application/json")


def get_users(request):
    """
    Returns the matching users and returns a list in JSON
    :type request: HttpRequest
    """
    if is_logged_in(request):
        if 'q' in request.GET and request.GET['q'] != '':
            if get_loggedin_user(request).role == BadgeUser.PROFESSOR:
                u = BadgeUser.get_matching_users(request.GET['q'])
                if u:
                    sugg = []
                    for user in u:
                        sugg.append({
                            'value': str(user.student_id) + ', ' + user.firstname + ' ' + user.lastname,
                            'data': user.id
                        })
                    result = {'error':False, 'suggestions': sugg}
                else:
                    result = {'error': True, 'msg': 'Kein User gefunden.', 'suggestions': []}
            else:
                result = {'error': True, 'msg': 'Sie haben nicht die n&ouml;tigen Rechte.', 'suggestions': []}
        else:
            result = {'error':True, 'msg':'Es fehlt ein Suchparameter.', 'suggestions': []}
    else:
        result = {'error': True, 'msg': 'Sie m&uuml;ssen eingeloggt sein.', 'suggestions': []}

    return HttpResponse(json.dumps(result), content_type="application/json")


def get_courses(request):
    """
    Tries to find matching courses and returns the resulting list as JSON
    :type request: HttpRequest
    """
    result = {}
    if 'q' in request.GET:
        q = request.GET['q']
        courses = []
        qm = re.match('^([0-9]{3})\.([0-9]{1,3})$', q);
        if qm:
            #tries to find a course by institute and course id
            for co in LVA.objects.filter(institute=int(qm.group(1)), number__startswith=int(qm.group(2))):
                courses.append({
                    'value': str(co.institute)+"."+str(co.number)+" "+co.title,
                    'data': {
                        'students': co.students,
                        'id': co.id
                    }
                })
        elif re.match('^[0-9]{1,3}\.?$', q):
            #tries to find courses by courseid
            for co in LVA.objects.filter(number__startswith=q.replace('.', '')):
                courses.append({
                    'value': str(co.institute)+"."+str(co.number)+" "+co.title,
                    'data': {
                        'students': co.students,
                        'id': co.id
                    }
                })
        else:
            #trues to find a course by matching the title
            for co in LVA.objects.filter(title__icontains=q):
                courses.append({
                    'value': str(co.institute)+"."+str(co.number)+" "+co.title,
                    'data': {
                        'students': co.students,
                        'id': co.id
                    }
                })
        result = {'error': False, 'suggestions': courses}
    else:
        result = {'error': True, 'msg': 'Es fehlt ein Parameter.', 'suggestions': []}

    return HttpResponse(json.dumps(result), content_type="application/json")
