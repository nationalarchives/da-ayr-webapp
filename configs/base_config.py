class BaseConfig(object):
    RATELIMIT_HEADERS_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    CONTACT_EMAIL = "contact email"
    CONTACT_PHONE = "contact phone"
    DEPARTMENT_NAME = "The National Archives"
    DEPARTMENT_URL = "https://www.nationalarchives.gov.uk/"
    SERVICE_NAME = "AYR - Access Your Records"
    SERVICE_PHASE = "BETA"
    SERVICE_URL = "https://ayr.nationalarchives.gov.uk/"
