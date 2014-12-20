from django.contrib.auth.models import Permission
from django.http import HttpResponse, HttpRequest
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from BadgePortfolio.models import *
from BadgePortfolio.login_handler import *
from random import choice
import json
import logging
import os
from os.path import isfile, join, isdir
import re
from datetime import date
from django.conf import settings


def issue_badge_form(request):
    """
    Returns the HTML for the badge issuing form
    :type request: HttpRequest
    """
    if is_logged_in(request):
        content = {
            'year': date.today().year
        }
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            if 'pid' in request.GET and request.GET['pid'] != '' and BadgePreset.objects.filter(id=request.GET['pid']).exists():
                bp = BadgePreset.objects.get(id=request.GET['pid'])
                content.update({
                    'p': bp,
                    'issuer': bu.firstname+' '+bu.lastname,
                    'issuer_id': bu.id
                })
                if 2 < date.today().month < 10:
                    content.update({
                        'candidates': BadgePresetSemesterCounts.count(date.today().year, Badge.SUMMER_SEMESTER, request.GET['pid'])
                    })
                else:
                    content.update({
                        'candidates': BadgePresetSemesterCounts.count(date.today().year, Badge.WINTER_SEMESTER, request.GET['pid'])
                    })

            if 2 < date.today().month < 10:
                content.update({
                    'summer_selected': ' selected="selected"'
                })
            else:
                content.update({
                    'winter_selected': ' selected="selected"'
                })
            return render_to_response('badge_form.html', content)
        else:
            return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
    else:
        return render_to_response('error.html', {'msg': 'Sie m&uuml;ssen eingeloggt sein.'})


def badge_detail(request):
    """
    Returns the HTML for the badge
    :type request: HttpRequest
    """
    if 'id' in request.GET and request.GET['id'] != '' and Badge.objects.filter(id=request.GET['id']).exists():
        b = Badge.objects.get(id=request.GET['id'])
        bu = get_loggedin_user(request)
        if b.public or (bu and b.awardee_id == bu.id):
            content = {
                'b': b,
                'proof': b.proof.replace('http://', '').replace('https://', ''),
                'link': re.match('^https?://', b.proof)
            }

            return render_to_response('badge_detail.html', content)
        else:
            return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
    else:
        return render_to_response('error.html', {'msg': 'Es fehlt ein Parameter oder dieser ist ung&uuml;ltig.'})


def badge_preset_form(request):
    """
    Returns the HTML for the badge preset form
    :type request: HttpRequest
    """
    if is_logged_in(request):
        content = {}
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            shapes = []
            shape_path = settings.SVG_FOLDER+'shapes/'
            for s in os.listdir(shape_path):
                if isfile(join(shape_path, s)):
                    shapes.append({
                        'url': join('images/shapes/', s),
                        'name': s.split('.')[0]
                    })

            patterns = []
            pattern_path = settings.SVG_FOLDER+'patterns/'
            for p in os.listdir(pattern_path):
                if isfile(join(pattern_path, p)):
                    p = p.replace('.svg', '')
                    patterns.append({
                        'url': '/bgsvg?p='+p,
                        'name': p
                    })

            content.update({
                'shapes': shapes,
                'patterns': patterns,
                'img': '',
                'save_label': 'Preset erstellen',
                'save_more_label': 'Preset und weiteres erstellen',
                'form_action_label': 'erstellen'
            })
            content.update(csrf(request))

            if 'id' in request.GET and request.GET['id'] != '' and BadgePreset.objects.filter(id=request.GET['id']).exists():
                bp = BadgePreset.objects.get(id=request.GET['id'])
                if bp.owner_id == bu.id:
                    if bp.issued_badges.count() == 0:
                        content.update({
                            'id': bp.id,
                            'name': bp.name,
                            'img': bp.img,
                            'keywords': bp.keywords,
                            'proof': bp.proof,
                            'comment': bp.comment,
                            'save_label': 'Preset speichern',
                            'save_more_label': 'Preset speichern und weiteres erstellen',
                            'form_action_label': 'editieren'
                        })

                        return render_to_response('badge_preset_form.html', content)
                    else:
                        return render_to_response('error.html', {'msg': 'Das Badge Preset wurde bereits verwendet und kann nicht mehr editiert werden.'})
                else:
                    return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
            else:
                return render_to_response('badge_preset_form.html', content)
        else:
            return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
    else:
        return render_to_response('error.html', {'msg': 'Sie m&uuml;ssen eingeloggt sein.'})


def badge_preset(request):
    """
    Returns the HTML for the badge preset
    :type request: HttpRequest
    """
    if is_logged_in(request):
        content = {}
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            if 'id' in request.GET and request.GET['id'] != '' and BadgePreset.objects.filter(id=request.GET['id']).exists():
                bp = BadgePreset.objects.get(id=request.GET['id'])
                if bp.owner_id == bu.id:
                    content.update({
                        'p': bp
                    })
                    return render_to_response('badge_preset.html', content)
                else:
                    return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
            else:
                return render_to_response('error.html', {'msg': 'Das Badge Preset existiert nicht.'})
        else:
            return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
    else:
        return render_to_response('error.html', {'msg': 'Sie m&uuml;ssen eingeloggt sein.'})


def badge_preset_detail(request):
    """
    Returns the HTML for the badge preset details
    :type request: HttpRequest
    """
    if is_logged_in(request):
        content = {}
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            if 'id' in request.GET and request.GET['id'] != '' and BadgePreset.objects.filter(id=request.GET['id']).exists():
                bp = BadgePreset.objects.get(id=request.GET['id'])
                if bp.owner_id == bu.id:
                    content.update({
                        'bp': bp,
                        'issued': bp.issued_badges.count()
                    })
                    return render_to_response('badge_preset_detail.html', content)
                else:
                    return render_to_response('error.html', {'msg': 'Sie haben nicht die n&ouml;tigen Rechte.'})
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
            if 'awardee_id' in request.POST and BadgeUser.objects.filter(id=request.POST['awardee_id']).exists():
                #if a user id is given
                awardee = BadgeUser.objects.get(id=request.POST['awardee_id'])
            elif 'awardee' in request.POST:
                # if no user id is given check if the name is a studentID and
                # create a new user if the studentID isn't already in use
                if re.match('^[0-9]{7}$', request.POST['awardee'], re.IGNORECASE):
                    if BadgeUser.objects.filter(student_id=request.POST['awardee']).exists():
                        awardee = BadgeUser.objects.get(student_id=request.POST['awardee'])

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
                if 'pid' in request.POST and BadgePreset.objects.filter(id=request.POST['pid']).exists():
                    bp = BadgePreset.objects.get(id=request.POST['pid'])
                    if bp.owner_id == bu.id:
                        if not awardee.my_badges.filter(preset_id=bp.id).exists():
                            b = Badge()
                            b.name = bp.name
                            b.img = bp.img
                            b.preset = bp
                        else:
                            result = {
                                'error': True,
                                'msg': 'Der Empf&auml;nger hat diesen Badge bereits.'
                            }
                    else:
                        result = {
                            'error': True,
                            'msg': 'Sie haben nicht die n&ouml;tigen Rechte um dieses Badge Preset zu verwenden.'
                        }
                #elif 'name' in request.POST and 'img' in request.POST:
                #    b = Badge()
                #    b.name = request.POST['name']
                #    b.img = request.POST['img']
                else:
                    result = {
                        'error': True,
                        'msg': 'Es fehlt ein Parameter'
                    }

                if b and 'rating' in request.POST and int(request.POST['rating']) >= 0 and int(request.POST['rating']) <= 3:
#TODO: sanity checking POST

                    b.awardee = awardee

                    if 'awarder' in request.POST and request.POST['awarder'] != '':
                        b.awarder = request.POST['awarder']
                    else:
                        b.awarder = bu.id

                    b.rating = int(request.POST['rating'])
                    b.issuer = bu

                    if 'semester' in request.POST and (request.POST['semester'] == Badge.WINTER_SEMESTER or request.POST['semester'] == Badge.SUMMER_SEMESTER) and 'year' in request.POST:
                        b.semester = request.POST['semester']
                        b.year = request.POST['year']
                    else:
                        b.year = date.today().year
                        if 2 < date.today().month < 10:
                            b.semester = Badge.SUMMER_SEMESTER
                        else:
                            b.semester = Badge.WINTER_SEMESTER

                    if 'comment' in request.POST:
                        b.comment = request.POST['comment']

                    if BadgePresetSemesterCounts.objects.filter(semester=b.semester, year=b.year, preset_id=b.preset_id).exists():
                        bpcc = BadgePresetSemesterCounts.objects.get(semester=b.semester, year=b.year, preset_id=b.preset_id);
                        if 'students' in request.POST and int(request.POST['students']) != bpcc.candidates and int(request.POST['students']) > b.preset.issued_badges.count():
                            bpcc.candidates = int(request.POST['students'])
                            bpcc.save()
                    else:
                        bpcc = BadgePresetSemesterCounts()
                        bpcc.year = b.year
                        bpcc.semester = b.semester
                        bpcc.preset = bp
                        if 'students' in request.POST and int(request.POST['students']) > b.preset.issued_badges.count():
                            bpcc.candidates = int(request.POST['students'])
                        else:
                            bpcc.candidates = b.preset.issued_badges.count() + 1
                        bpcc.save()

                    b.candidates = bpcc.candidates

                    b.proof = request.POST['proof']

                    if 'lva_id' not in request.POST or request.POST['lva_id'] == '':
                        if 'lva' in request.POST and request.POST['lva'] != '':
                            lvap = re.match('^([0-9]{3})\.([0-9]{3}) ?(.+)$', request.POST['lva'])
                            if lvap:
                                #check if lva exists already
                                if LVA.objects.filter(institute=lvap.group(1), number=lvap.group(2)).exists():
                                    b.lva = LVA.objects.get()
                                else:
                                    lva = LVA()
                                    lva.title = lvap.group(3)
                                    lva.institute = lvap.group(1)
                                    lva.number = lvap.group(2)
                                    if 'students' in request.POST:
                                        lva.students = request.POST['students']
                                    else:
                                        lva.students = 1
                                    lva.save()
                                    b.lva = lva
                            else:
                                b.context = request.POST['lva']
                    else:
                        b.lva = LVA.objects.get(id=request.POST['lva_id'])

                    b.save()

                    if bp:
                        b.keywords = bp.keywords.all()

                    if 'keywords' in request.POST:
                        kw = request.POST['keywords'].split(',')
                        for k in kw:
                            k = k.strip()
                            if Tag.objects.filter(name=k).exists():
                                ko = Tag.objects.get(name=k)
                            else:
                                ko = Tag()
                                ko.name = k
                                ko.save()
                            b.keywords.add(ko)

                    b.save()

                    result = {
                        'error': False,
                        'id': b.id
                    }
                elif 'error' not in result:
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
            if 'id' in request.POST and request.POST['id'] != '':
                if BadgePreset.objects.filter(id=request.POST['id']).exists():
                    bp = BadgePreset.objects.get(id=request.POST['id'])
                    if bp.owner_id != bu.id:
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
                bp.owner = bu

            if bp:

                if not bp.id or bp.issued_badges.count() == 0:
                    if 'name' in request.POST:
                        bp.name = request.POST['name']
                    if 'img' in request.POST:
                        bp.img = request.POST['img']
                    if 'proof' in request.POST:
                        bp.proof = request.POST['proof']
                    if 'comment' in request.POST:
                        bp.comment = request.POST['comment']

                    bp.save()

                    if 'keywords' in request.POST and request.POST['keywords'] != '':
                        kw = request.POST['keywords'].split(',')
                        for k in kw:
                            k = k.strip()
                            if Tag.objects.filter(name=k).exists():
                                ko = Tag.objects.get(name=k)
                            else:
                                ko = Tag()
                                ko.name = k
                                ko.save()
                            bp.keywords.add(ko)

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
            if 'id' in request.POST and request.POST['id'] != '' and BadgePreset.objects.filter(id=request.POST['id']).exists():
                bp = BadgePreset.objects.get(id=request.POST['id'])
                if bp.owner_id == bu.id:
                    bpn = BadgePreset()
                    bpn.name = bp.name + "*"
                    bpn.img = bp.img
                    bpn.owner = bp.owner
                    bpn.save()
                    bpn.original = bp
                    bpn.keywords = bp.keywords.all()
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


def delete_badge_preset(request):
    """
    Tries to delete the requested badge preset and returns a JSON response
    :type request: HttpRequest
    """
    result = {'error': True, 'msg': ''}

    if is_logged_in(request):
        bu = get_loggedin_user(request)
        if bu.role == BadgeUser.PROFESSOR:
            if 'id' in request.POST and request.POST['id'] != '' and BadgePreset.objects.filter(id=request.POST['id']).exists():
                bp = BadgePreset.objects.get(id=request.POST['id'])
                if bp.owner_id == bu.id:
                    if bp.issued_badges.count() == 0:
                        bp.delete()
                    #else:
                        #TODO hide preset if already used

                    result = {
                        'error': False,
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
        if 'id' in request.POST and request.POST['id'] != '' and Badge.objects.filter(id=request.POST['id']).exists():
            badge = Badge.objects.get(id=request.POST['id'])
            if badge.awardee.id == get_loggedin_user(request).id:
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


def get_users(request, students=False):
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
                        if (not students or user.role == BadgeUser.STUDENT) and ('pid' not in request.GET or not user.my_badges.filter(preset_id=request.GET['pid']).exists()):
                            sugg.append({
                                'value': str(user.student_id) + ', ' + user.firstname + ' ' + user.lastname,
                                'data': user.id
                            })
                    if len(sugg) > 0:
                        result = {'error': False, 'suggestions': sugg}
                    else:
                        result = {'error': True, 'msg': 'Kein User gefunden.', 'suggestions': []}
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
        qm = re.match('^([0-9]{3})\.([0-9]{1,3}).*$', q);
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


def get_tags(request):
    """
    Tries to find matching tags and returns the resulting list as JSON
    :type request: HttpRequest
    """
    result = {}
    if 'q' in request.GET:
        q = request.GET['q']
        tags = []

        for t in Tag.objects.filter(name__icontains=q):
            tags.append({
                'value': t.name,
                'data': {
                    'id': t.id
                }
            })

        result = {'error': False, 'suggestions': tags}
    else:
        result = {'error': True, 'msg': 'Es fehlt ein Parameter.', 'suggestions': []}

    return HttpResponse(json.dumps(result), content_type="application/json")


def get_candidate_count(request):
    """
    Tries to retrieve the count for the given BadgePreset, semester and year returns the resulting list as JSON
    :type request: HttpRequest
    """
    result = {}
    if 'y' in request.GET and 's' in request.GET and 'id' in request.GET:
        result = {'error': False, 'count': BadgePresetSemesterCounts.count(request.GET['y'], request.GET['s'], request.GET['id'])}
    else:
        result = {'error': True, 'msg': 'Es fehlt ein Parameter.', 'count': 0}

    return HttpResponse(json.dumps(result), content_type="application/json")
