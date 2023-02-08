from django.urls import path, include

from . import views

urlpatterns = [
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", views.index),
    path("departments/<str:name>/records", views.DepartmentRecordsView.as_view()),
    path("departments/<str:name>/metadata", views.DepartmentMetadataView.as_view()),
]
