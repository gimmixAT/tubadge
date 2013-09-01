from django.http import HttpResponse, HttpRequest
from django.shortcuts import render_to_response
from xml.dom import minidom
from django.template import loader, Context
import re

def build_svg(request):
    """
    :type request: HttpRequest
    """

    shape = 'fire'
    pattern = 'checker'
    color = '#ff00ff'

    if 's' in request.GET:
        shape = request.GET['s']

    if 'p' in request.GET:
        pattern = request.GET['p']

    if 'c' in request.GET:
        color = '#'+request.GET['c']

    pattern_dom = minidom.parse('./static/images/patterns/'+pattern+'.svg')
    shape_dom = minidom.parse('./static/images/shapes/'+shape+'.svg')
    pattern_root = pattern_dom.documentElement;
    shape_root = shape_dom.documentElement;

    content = {
        'pattern': pattern_root.toxml(),
        'pattern_width': pattern_root.getAttribute('width'),
        'pattern_height': pattern_root.getAttribute('height'),
        'shape': re.sub(r'(fill|stroke):#[a-f0-9]{6}', r'\1:'+color, re.sub(r'(fill|stroke)="#[a-f0-9]{6}"', r'\1="'+color+'"', shape_root.toxml(), flags=re.IGNORECASE), flags=re.IGNORECASE),
        'shape_width': shape_root.getAttribute('width').replace('px', ''),
        'shape_height': shape_root.getAttribute('height').replace('px', '')
    }

    t = loader.get_template('svg_base.svg')
    cont = Context(content)
    rendered = t.render(cont)

    return  HttpResponse(rendered, content_type="image/svg+xml")