from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import loader


def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({}, request))
