from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.template import loader
from django.views import View


def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({}, request))


class SearchView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        search_term = request.POST['search_term']
        result = open_search(search_term)
        # s3://departments/a/secretfile
        # departments/a/records/secretfile

        context = {"result": result}
        return render(request, template_name="search.html", context=context)

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, template_name="search.html")


class DepartmentBaseView(UserPassesTestMixin, View):
    raise_exception = True

    @property
    def name(self):
        return self.kwargs["name"]

    def test_func(self) -> bool:
        return self.request.user.groups.filter(name=f"department_{self.name}").exists()


def open_search(search_term):
    return [{"key": search_term}]


class DepartmentRecordsView(DepartmentBaseView):
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {"department_name": self.name}
        return render(request, template_name="records.html", context=context)


class DepartmentMetadataView(DepartmentBaseView):
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {"department_name": self.name}
        return render(request, template_name="metadata.html", context=context)


class DepartmentRecordDetailView(DepartmentBaseView):
    @property
    def record_name(self):
        return self.kwargs['record_name']

    def get(self, request: HttpRequest, *args, **kwargs):
        context = {"department_name": self.name}
        # boto3 get_record(department_name, self.record_name)
        return render(request, template_name="metadata.html", context=context)
