from django.contrib import admin
from django.urls import path, include
from mozilla_django_oidc.views import OIDCAuthenticationRequestView, OIDCLogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('login/', OIDCAuthenticationRequestView.as_view(), name='oidc_login'),
    path('logout/', OIDCLogoutView.as_view(), name='oidc_logout'),
    path("oidc/", include('mozilla_django_oidc.urls')),
]
