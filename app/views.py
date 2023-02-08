from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views import View


def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({}, request))


class DepartmentBaseView(UserPassesTestMixin, View):
    raise_exception = True

    def name(self):
        return self.kwargs["name"]

    def test_func(self) -> bool:
        return self.request.user.groups.filter(name=f"department_{self.name}").exists()


class DepartmentRecordsView(DepartmentBaseView):
    def get(self, request, *args, **kwargs):
        context = {"department_name": self.name}
        return render(request, template_name="records.html", context=context)


class DepartmentMetadataView(DepartmentBaseView):
    def get(self, request, *args, **kwargs):
        context = {"department_name": self.name}
        return render(request, template_name="metadata.html", context=context)
