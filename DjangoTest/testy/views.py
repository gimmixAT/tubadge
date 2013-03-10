from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response

def index(request):
    # c = Context({
    #     'msg': 'lol oh hai!',
    # })
    # return HttpResponse(loader.get_template('hello_world.html').render(c))

    return render_to_response('hello_world.html', {'msg' : 'lol wie gehts?'})