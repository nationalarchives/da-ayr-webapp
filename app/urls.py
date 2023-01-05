from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index),
    path("oidc/", include("mozilla_django_oidc.urls")),
]
