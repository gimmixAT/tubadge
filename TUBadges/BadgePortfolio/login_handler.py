from django.http import HttpResponseRedirect
from django.utils.crypto import salted_hmac
import time
from BadgePortfolio.models import BadgeUser


def authenticate(request):
    """
    :param request:
    :type request: django.http.HttpRequest
    """
    secret = "asdjasldkjlasdiu7sa7df9qr98a7doasd897a89s0d798fjkxhc"
    if request.GET['sKey']: hmac = request.GET['sKey']
    if request.GET['logout']: hmac = request.GET['logout']
    now = int(time.time() / 10)
    values = ''
    for v in ['oid', 'mn', 'firstName', 'lastName', 'mail']:
        values = values + request.GET[v]

    for offset in [0, -1, 1, -2, 2]:
        if salted_hmac(None,values + (now + offset), secret) == hmac:
            return True

    return False


def handle_login(request):
    """
    :param request:
    :type request: django.http.HttpRequest
    """
    #check if user already exists
    if not BadgeUser.objects.filter('mail', request.GET['mail']).exists():
        #create new user if first login
        bu = BadgeUser(
            firstname=request.GET['firstName'],
            lastname=request.GET['lastName'],
            email=request.GET['mail'],
            student_id=request.GET['mn'])
        bu.save()
        request.session['sKey'] = request.GET['sKey']
        request.session['uID'] = bu.id
        return True
    else:
        bu = BadgeUser.objects.filter('mail', request.GET['mail'])
        request.session['sKey'] = request.GET['sKey']
        request.session['uID'] = bu.id
        return False


def handle_logout(request):
    """
    :param request:
    :type request: django.http.HttpRequest
    """
    del request.session['sKey']
    del request.session['uID']
    return HttpResponseRedirect('https://iu.zid.tuwien.ac.at/0.graphic.check')