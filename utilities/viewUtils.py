__author__ = 'swolfod'

from rest_framework.response import Response
from utilities import djangoUtils
from django.conf import settings


FAKE_DATA = getattr(settings, 'FAKE_DATA', False)


def viewResponse(context=None, content_type=None):
    return Response(djangoUtils.ajaxResponse(context if context else {}), content_type=content_type)


def viewErrorResponse(errMsg, errCode=None):
    return Response(djangoUtils.ajaxErrorResponse(errMsg, errCode))


def getPagePosition(request, defaultCount=24):
    start = request.GET.get("start")
    if start is not None:
        last = ""
        start = int(start)
    else:
        last = request.GET.get("last", "")
        start = 0

    count = int(request.GET.get("count", defaultCount))

    return last, start, count
