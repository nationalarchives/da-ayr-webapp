from .settings import KEYCLOACK_REALM_BASE_URI


def provider_logout(request):
    return f'{KEYCLOACK_REALM_BASE_URI}/protocol/openid-connect/logout'
