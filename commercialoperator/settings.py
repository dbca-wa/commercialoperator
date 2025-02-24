from django.core.exceptions import ImproperlyConfigured

import os, hashlib
import confy
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
confy.read_environment_file(BASE_DIR+"/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

from ledger.settings_base import *

ROOT_URLCONF = 'commercialoperator.urls'
SITE_ID = 1
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
SYSTEM_MAINTENANCE_WARNING = env('SYSTEM_MAINTENANCE_WARNING', 24) # hours
DISABLE_EMAIL = env('DISABLE_EMAIL', False)
SHOW_TESTS_URL = env('SHOW_TESTS_URL', False)
SHOW_DEBUG_TOOLBAR = env('SHOW_DEBUG_TOOLBAR', False)
BUILD_TAG = env('BUILD_TAG', hashlib.md5(os.urandom(32)).hexdigest())  # URL of the Dev app.js served by webpack & express
VERSION_NO = '1.0.1'

if env('CONSOLE_EMAIL_BACKEND', False):
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SHOW_ROOT_API = env('SHOW_ROOT_API', False)

if SHOW_DEBUG_TOOLBAR:
#    def get_ip():
#        import subprocess
#        route = subprocess.Popen(('ip', 'route'), stdout=subprocess.PIPE)
#        network = subprocess.check_output(
#            ('grep', '-Po', 'src \K[\d.]+\.'), stdin=route.stdout
#        ).decode().rstrip()
#        route.wait()
#        network_gateway = network + '1'
#        return network_gateway

    def show_toolbar(request):
        return True

    MIDDLEWARE_CLASSES += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        #'whitenoise.middleware.WhiteNoiseMiddleware',
    ]
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    #INTERNAL_IPS = ('127.0.0.1', 'localhost', get_ip())
    INTERNAL_IPS = ('127.0.0.1', 'localhost')

    # this dict removes check to dtermine if toolbar should display --> works for rks docker container
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
        'INTERCEPT_REDIRECTS': False,
    }

STATIC_URL = '/static/'


INSTALLED_APPS += [
    'reversion_compare',
    'bootstrap3',
    'commercialoperator',
    'commercialoperator.components.main',
    'commercialoperator.components.organisations',
    'commercialoperator.components.users',
    'commercialoperator.components.proposals',
    'commercialoperator.components.approvals',
    'commercialoperator.components.compliances',
    'commercialoperator.components.bookings',
    'taggit',
    'rest_framework',
    'rest_framework_datatables',
    'rest_framework_gis',
    'reset_migrations',
    'ckeditor',
    'multiselectfield',
    'appmonitor_client',
]

ADD_REVERSION_ADMIN=True

# maximum number of days allowed for a booking
WSGI_APPLICATION = 'commercialoperator.wsgi.application'

'''REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'commercialoperator.perms.OfficerPermission',
    )
}'''

#REST_FRAMEWORK = {
#    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
#    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#        'PAGE_SIZE': 5
#}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    #'DEFAULT_FILTER_BACKENDS': (
    #    'rest_framework_datatables.filters.DatatablesFilterBackend',
    #),
    #'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    #'PAGE_SIZE': 20,
}


MIDDLEWARE_CLASSES += [
    'commercialoperator.middleware.BookingTimerMiddleware',
    'commercialoperator.middleware.FirstTimeNagScreenMiddleware',
    'commercialoperator.middleware.RevisionOverrideMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'commercialoperator', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'commercialoperator','components','organisations', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'commercialoperator','components','emails', 'templates'))
del BOOTSTRAP3['css_url']
#BOOTSTRAP3 = {
#    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
#    'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
#    'css_url': None,
#    'theme_url': None,
#    'javascript_url': None,
#    'javascript_in_head': False,
#    'include_jquery': False,
#    'required_css_class': 'required-form-field',
#    'set_placeholder': False,
#}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'commercialoperator', 'cache'),
    }
}
STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles_co')
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'commercialoperator', 'static')))
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'commercialoperator', 'static', 'commercialoperator_vue', 'static')))
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
if DEV_STATIC and not DEV_STATIC_URL:
    raise ImproperlyConfigured('If running in DEV_STATIC, DEV_STATIC_URL has to be set')
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Department details
SYSTEM_NAME = env('SYSTEM_NAME', 'Commercial Operator Licensing')
SYSTEM_NAME_SHORT = env('SYSTEM_NAME_SHORT', 'COLS')
SITE_PREFIX = env('SITE_PREFIX')
SITE_DOMAIN = env('SITE_DOMAIN')
SUPPORT_EMAIL = env('SUPPORT_EMAIL', 'licensing@' + SITE_DOMAIN).lower()
SUPPORT_EMAIL_FILMING = env('SUPPORT_EMAIL_FILMING', 'filming@' + SITE_DOMAIN).lower()
DEP_URL = env('DEP_URL','www.' + SITE_DOMAIN)
DEP_PHONE = env('DEP_PHONE','(08) 9219 9978')
DEP_PHONE_FILMING = env('DEP_PHONE_FILMING','(08) 9219 8411')
DEP_PHONE_SUPPORT = env('DEP_PHONE_SUPPORT','(08) 9219 9000')
DEP_FAX = env('DEP_FAX','(08) 9423 8242')
DEP_POSTAL = env('DEP_POSTAL','Locked Bag 104, Bentley Delivery Centre, Western Australia 6983')
DEP_NAME = env('DEP_NAME','Department of Biodiversity, Conservation and Attractions')
DEP_NAME_SHORT = env('DEP_NAME_SHORT','DBCA')
BRANCH_NAME = env('BRANCH_NAME','Tourism and Concessions Branch')
DEP_ADDRESS = env('DEP_ADDRESS','17 Dick Perry Avenue, Kensington WA 6151')
SITE_URL = env('SITE_URL', 'https://' + SITE_PREFIX + '.' + SITE_DOMAIN)
PUBLIC_URL=env('PUBLIC_URL', SITE_URL)
PUBLIC_URL=PUBLIC_URL if PUBLIC_URL.endswith(os.sep) else PUBLIC_URL + os.sep
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'no-reply@' + SITE_DOMAIN).lower()
MEDIA_APP_DIR = env('MEDIA_APP_DIR', 'cols')
ADMIN_GROUP = env('ADMIN_GROUP', 'COLS Admin')
COLS_EVENT_USERGUIDE_URL = env('COLS_EVENT_USERGUIDE_URL', 'https://parks.dpaw.wa.gov.au/for-business/how-apply-0')
COLS_HANDBOOK_URL = env('COLS_HANDBOOK_URL', 'https://parks.dpaw.wa.gov.au/know/commercial-operator-handbook')
COLS_FILMING_HANDBOOK_URL = env('COLS_FILMING_HANDBOOK_URL', 'https://parks.dpaw.wa.gov.au/know/commercial-filming-and-photography-handbook')
CRON_RUN_AT_TIMES = env('CRON_RUN_AT_TIMES', '04:05')
CRON_EMAIL = env('CRON_EMAIL', 'cron@' + SITE_DOMAIN).lower()
# for ORACLE Job Notification - override settings_base.py
EMAIL_FROM = DEFAULT_FROM_EMAIL
OTHER_PAYMENT_ALLOWED = env('OTHER_PAYMENT_ALLOWED', False) # Cash/Cheque

OSCAR_BASKET_COOKIE_OPEN = 'cols_basket'
PAYMENT_SYSTEM_ID = env('PAYMENT_SYSTEM_ID', 'S557')
PS_PAYMENT_SYSTEM_ID = PAYMENT_SYSTEM_ID
PAYMENT_SYSTEM_PREFIX = env('PAYMENT_SYSTEM_PREFIX', PAYMENT_SYSTEM_ID.replace('S','0')) # '0557'
os.environ['LEDGER_PRODUCT_CUSTOM_FIELDS'] = "('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code')"
CRON_NOTIFICATION_EMAIL = env('CRON_NOTIFICATION_EMAIL', NOTIFICATION_EMAIL).lower()
VERSION_NO="1.0.1"
DEV_APP_BUILD_URL=env('DEV_APP_BUILD_URL')

TIME_ZONE='Australia/Perth'


if not VALID_SYSTEMS:
    VALID_SYSTEMS = [PAYMENT_SYSTEM_ID]

CRON_CLASSES = [
    'commercialoperator.cron.OracleIntegrationCronJob',
    #'appmonitor_client.cron.CronJobAppMonitorClient',
]


BASE_URL=env('BASE_URL')

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        #'width': 300,
        'width': '100%',
    },
    'awesome_ckeditor': {
        'toolbar': 'Basic',
    },
}

# Additional logging for commercialoperator
LOGGING['handlers']['payment_checkout'] = {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'cols_payment_checkout.log'),
            'formatter': 'verbose',
            'maxBytes': 5242880
        }
LOGGING['loggers']['payment_checkout'] = {
            'handlers': ['payment_checkout'],
            'level': 'INFO'
        }

LOGGING['loggers']['commercialoperator'] = {
            'handlers': ['file'],
            'level': 'INFO'
        }


