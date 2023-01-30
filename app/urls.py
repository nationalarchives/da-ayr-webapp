from django.urls import path, include

from . import views

urlpatterns = [
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", views.index),
    path("department/<str:name>/records", views.records),
    path("department/<str:name>/metadata", views.metadata),
]
