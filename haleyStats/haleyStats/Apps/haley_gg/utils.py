import gspread
import os

from oauth2client.service_account import ServiceAccountCredentials
from gspread.utils import NoValidUrlKeyFound

"""
1.  Invite account in spreadsheet with viewer.
    account is specified in gspread-key.json

2.  Get spreadsheet file name from FormView.

3.  Load sheet.

"""


def get_spreadsheet(url):
    try:
        scope = ['https://www.googleapis.com/auth/drive']
        DIRNAME = os.path.dirname(__file__)
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.path.join(DIRNAME, 'gspread-key.json'), scope)
        gc = gspread.authorize(credentials)
        # 문서 불러오기
        doc = gc.open_by_url(url)
        return doc
    except NoValidUrlKeyFound:
        raise NoValidUrlKeyFound
