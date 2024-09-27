from ast import Not
import functools
import logging
import traceback

from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


def basic_exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            raise serializers.ValidationError(e)
        except serializers.ValidationError as e:
            raise e
        except NotImplementedError as e:
            raise APIException(code=501, detail=str(e))
        except Exception as e:
            if settings.DEBUG:
                detail = {
                    "user message (settings.API_EXCEPTION_MESSAGE)": settings.API_EXCEPTION_MESSAGE,
                    "type": type(e),
                    "error": str(e),
                    "stacktrace": traceback.format_exc(),
                }
                raise APIException(code=500, detail=detail)
            # Don't send complex exception messages to the client when in production
            raise APIException(settings.API_EXCEPTION_MESSAGE)

    return wrapper
