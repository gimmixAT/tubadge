from django.http import HttpResponseRedirect, HttpRequest
import time
from datetime import datetime
from BadgePortfolio.models import BadgeUser
from django.conf import settings
import hashlib
import hmac

def check_if_login(request):
    """
    :type request: HttpRequest
    """
    if 'uID' in request.session and request.session['uID'] != '' and not BadgeUser.objects.filter(id=request.session['uID']).exists():
        del request.session['uID']
    if 'pw' in request.POST and request.POST['pw'] != '' and 'mail' in request.POST and request.POST['mail'] != '':
        if BadgeUser.objects.filter(email=request.POST['mail']).exists():
            bu = BadgeUser.objects.filter(email=request.POST['mail'])[0]
            if bu.check_password(request.POST['pw']):
                request.session['uID'] = bu.id
            else:
                request.session['login_msg'] = "Falsches Passwort."
        else:
            request.session['login_msg'] = "Der User existiert nicht."

    elif 'sKey' in request.GET or 'logout' in request.GET:
        if authenticate(request):
            if request.GET['sKey']:
                handle_login(request)
            else:
                return handle_logout(request, True)
        else:
            handle_logout(request)


def get_loggedin_user(request):
    if 'uID' in request.session:
        return BadgeUser.objects.get(id=request.session['uID'])
    else:
        return None


def is_logged_in(request):
    """
    :type request: HttpRequest
    """
    if 'uID' in request.session and request.session['uID'] != '':
        return True
    else:
        return False


def authenticate(request):
    """
    :param request:
    :type request: HttpRequest
    """
    #secret = "asdjasldkjlasdiu7sa7df9qr98a7doasd897a89s0d798fjkxhc"
    if 'sKey' in request.GET:
        skey = request.GET['sKey']
    if 'logout' in request.GET:
        skey = request.GET['logout']
    now = int(time.time() / 10)
    values = ''
    for v in ['oid', 'mn', 'firstName', 'lastName', 'mail', 'orgs']:
        if v in request.GET: values += request.GET[v]

    for offset in [0, -1, 1, -2, 2]:
        if hmac.new(settings.SSO_SECRET.encode(encoding='latin1'), (values + str(now + offset)).encode(encoding='latin1'), hashlib.sha1).hexdigest() == skey:
            return True

    return False


def handle_login(request):
    """
    :param request:
    :type request: HttpRequest
    """
    #check if user already exists
    if not BadgeUser.objects.filter(object_id=request.GET['oid']).exists():
        #check if dummy user is already in the system
        if BadgeUser.objects.filter(student_id=request.GET['mn']).exists():
            bu = BadgeUser.objects.filter(student_id=request.GET['mn'])
            bu.firstname = request.GET['firstName']
            bu.lastname = request.GET['lastName']
            bu.email = request.GET['mail']
            bu.object_id = request.GET['oid']
        else:
            #create new user if first login and no dummy user exists
            bu = BadgeUser(
                firstname=request.GET['firstName'],
                lastname=request.GET['lastName'],
                email=request.GET['mail'],
                student_id=request.GET['mn'],
                object_id=request.GET['oid'])
        bu.save()
        request.session['sKey'] = request.GET['sKey']
        request.session['uID'] = bu.id
        request.session['last_action_date'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        return True
    else:
        bu = BadgeUser.objects.get(object_id=request.GET['oid'])
        request.session['sKey'] = request.GET['sKey']
        request.session['uID'] = bu.id
        request.session['last_action_date'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        return False


def handle_logout(request, force=False):
    """
    :param request:
    :type request: HttpRequest
    """
    if 'sKey' in request.session: del request.session['sKey']
    if 'uID' in request.session: del request.session['uID']
    request.session.flush()

    if force and 'oid' in request.GET:
        bu = BadgeUser.objects.get(object_id=request.GET['oid'])
        if bu:
            bu.logout_date = datetime.utcnow()
            bu.save()

    return HttpResponseRedirect('https://iu.zid.tuwien.ac.at/0.graphic.check')


def update_session(request):
    """
    Checks if the user has already been logged out in the meantime via SSO
    :param request:
    :type request: HttpRequest
    """
    if 'uID' in request.session and request.session['uID'] != '':
        bu = BadgeUser.objects.get(id=request.session['uID'])
        if 'last_action_date' in request.session and bu.logout_date and datetime.strptime(bu.logout_date.strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f') > datetime.strptime(request.session['last_action_date'], '%Y-%m-%d %H:%M:%S.%f'):
            handle_logout(request)
        else:
            request.session['last_action_date'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
