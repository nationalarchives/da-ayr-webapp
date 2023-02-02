from django.urls import path, include

from . import views

urlpatterns = [
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", views.index),
    path("departments/a/records", views.DepartmentARecordsView.as_view()),
    path("departments/a/metadata", views.DepartmentAMetadataView.as_view()),
    path("departments/b/records", views.DepartmentBRecordsView.as_view()),
    path("departments/b/metadata", views.DepartmentBMetadataView.as_view()),
    path("departments/c/records", views.DepartmentCRecordsView.as_view()),
    path("departments/c/metadata", views.DepartmentCMetadataView.as_view()),
]
