from django.http import HttpResponseRedirect, HttpRequest
from django.utils.crypto import salted_hmac
import time
from BadgePortfolio.models import BadgeUser


def check_if_login(request):
    """
    :type request: HttpRequest
    """
    if 'uID' in request.session and request.session['uID'] != '' and not BadgeUser.objects.filter(id=request.session['uID']).exists():
        del request.session['uID']
    if 'pw' in request.POST and 'mail' in request.POST:
        if BadgeUser.objects.filter(email=request.POST['mail']).exists():
            bu = BadgeUser.objects.filter(email=request.POST['mail'])[0]
            if bu.check_password(request.POST['pw']):
                request.session['uID'] = bu.id

    elif 'sKey' in request.GET or 'logout' in request.GET:
        if authenticate(request):
            if request.GET['sKey']: handle_login(request)
            else: return handle_logout(request)
        else: handle_logout(request)


def get_loggedin_user(request):
    return BadgeUser.objects.get(id=request.session['uID'])


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
    secret = "asdjasldkjlasdiu7sa7df9qr98a7doasd897a89s0d798fjkxhc"
    if 'sKey' in request.GET: hmac = request.GET['sKey']
    if 'logout' in request.GET: hmac = request.GET['logout']
    now = int(time.time() / 10)
    values = ''
    for v in ['oid', 'mn', 'firstName', 'lastName', 'mail']:
        if v in request.GET: values = ''.join(values, request.GET[v])

    for offset in [0, -1, 1, -2, 2]:
        if salted_hmac('', values + str(now + offset), secret) == hmac:
            return True

    return False


def handle_login(request):
    """
    :param request:
    :type request: HttpRequest
    """
    #check if user already exists
    if not BadgeUser.objects.filter(object_id=request.GET['oid']).exists():
        #create new user if first login
        bu = BadgeUser(
            firstname=request.GET['firstName'],
            lastname=request.GET['lastName'],
            email=request.GET['mail'],
            student_id=request.GET['mn'],
            object_id=request.GET['oid'])
        bu.save()
        request.session['sKey'] = request.GET['sKey']
        request.session['uID'] = bu.id
        return True
    else:
        bu = BadgeUser.objects.filter(object_id=request.GET['oid'])
        request.session['sKey'] = request.GET['sKey']
        request.session['uID'] = bu.id
        return False


def handle_logout(request):
    """
    :param request:
    :type request: HttpRequest
    """
    if 'sKey' in request.session: del request.session['sKey']
    del request.session['uID']
    return HttpResponseRedirect('https://iu.zid.tuwien.ac.at/0.graphic.check')