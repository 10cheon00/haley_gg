from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from gspread.utils import NoValidUrlKeyFound
from gspread.client import APIError

from .models import User
from .utils import get_spreadsheet
"""
1.  Invite account in spreadsheet with viewer.
    account is specified in gspread-key.json

2.  Get spreadsheet file name from FormView.

3.  Load sheet.

"""


def load_document(url):
    try:
        doc = get_spreadsheet(url)
        # a 시트 불러오기
        if doc.worksheet('개인전적Data') and doc.worksheet('팀플전적Data'):
            return doc
    except NoValidUrlKeyFound:
        msg = u"스프레드시트가 아닙니다."
        raise ValidationError(msg)
    except APIError:
        msg = u"전적 데이터가 없는 시트입니다."
        raise ValidationError(msg)


def search_user(name):
    try:
        user = User.objects.get(name__iexact=name)
        return user
    except ObjectDoesNotExist:
        msg = u"존재하지 않는 유저입니다."
        raise ValidationError(msg)
