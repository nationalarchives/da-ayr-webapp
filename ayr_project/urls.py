from django.contrib import admin
from django.urls import path, include
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, OIDCLogoutView

from ayr_project import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index),
    path("oidc/", include('mozilla_django_oidc.urls')),
]
