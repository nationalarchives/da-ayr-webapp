from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views import View


def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({}, request))


class DepartmentRecordsBaseView(UserPassesTestMixin, View):
    name = None
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name=f"department_{self.name}").exists()

    def get(self, request, *args, **kwargs):
        context = {"department_name": self.name}
        return render(request, template_name="records.html", context=context)


class DepartmentMetadataBaseView(UserPassesTestMixin, View):
    name = None
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name=f"department_{self.name}").exists()

    def get(self, request, *args, **kwargs):
        context = {"department_name": self.name}
        return render(request, template_name="metadata.html", context=context)


class DepartmentARecordsView(DepartmentRecordsBaseView):
    name = "a"


class DepartmentAMetadataView(DepartmentMetadataBaseView):
    name = "a"


class DepartmentBRecordsView(DepartmentRecordsBaseView):
    name = "b"


class DepartmentBMetadataView(DepartmentMetadataBaseView):
    name = "b"


class DepartmentCRecordsView(DepartmentRecordsBaseView):
    name = "c"


class DepartmentCMetadataView(DepartmentMetadataBaseView):
    name = "c"
