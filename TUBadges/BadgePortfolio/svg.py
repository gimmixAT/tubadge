from django.http import HttpResponse, HttpRequest
from django.shortcuts import render_to_response
from xml.dom import minidom
from django.template import loader, Context
import re
from os.path import exists
from django.conf import settings


def build_svg(request):
    """
    :type request: HttpRequest
    """

    shape = 'fire'
    pattern = 'checker'
    color = '#ff00ff'

    if 's' in request.GET and request.GET['s'] != '' and exists(settings.SVG_FOLDER+'shapes/'+request.GET['s']+'.svg'):
        shape = request.GET['s']

    if 'p' in request.GET and request.GET['p'] != '' and exists(settings.SVG_FOLDER+'patterns/'+request.GET['p']+'.svg'):
        pattern = request.GET['p']

    if 'c' in request.GET and request.GET['c'] != '':
        color = '#'+request.GET['c']

    pattern_dom = minidom.parse(settings.SVG_FOLDER+'patterns/'+pattern+'.svg')
    shape_dom = minidom.parse(settings.SVG_FOLDER+'shapes/'+shape+'.svg')
    pattern_root = pattern_dom.documentElement;
    shape_root = shape_dom.documentElement;

    content = {
        'pattern': pattern_root.toxml(),
        'pattern_width': pattern_root.getAttribute('width'),
        'pattern_height': pattern_root.getAttribute('height'),
        'shape': re.sub(r'(fill|stroke):#[a-f0-9]{6}', r'\1:'+color, re.sub(r'(fill|stroke)="#[a-f0-9]{6}"', r'\1="'+color+'"', shape_root.toxml(), flags=re.IGNORECASE), flags=re.IGNORECASE),
        'shape_width': int(float(shape_root.getAttribute('width').replace('px', '')))+2,
        'shape_height': int(float(shape_root.getAttribute('height').replace('px', '')))+2
    }

    t = loader.get_template('svg_base.svg')
    cont = Context(content)
    rendered = t.render(cont)

    return HttpResponse(rendered, content_type="image/svg+xml")


def build_bg_svg(request):
    """
    :type request: HttpRequest
    """

    pattern = 'checker'

    if 'p' in request.GET:
        pattern = request.GET['p']

    pattern_dom = minidom.parse(settings.SVG_FOLDER+'patterns/'+pattern+'.svg')
    pattern_root = pattern_dom.documentElement;

    content = {
        'pattern': pattern_root.toxml(),
        'pattern_width': pattern_root.getAttribute('width'),
        'pattern_height': pattern_root.getAttribute('height')
    }

    t = loader.get_template('svg_bgpreview.svg')
    cont = Context(content)
    rendered = t.render(cont)

    return HttpResponse(rendered, content_type="image/svg+xml")