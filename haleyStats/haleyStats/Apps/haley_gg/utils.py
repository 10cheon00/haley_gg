import datetime
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


def get_match_data_from_match_list(match_result):
    match_data_dict = {}

    # if match_result's item is empty data,
    # fill it with 'Empty Data'.
    for index, value in enumerate(match_result):
        if value == '':
            match_result[index] = "Empty data."

    # match date
    date = match_result[0]
    date = date.split('.')
    if len(date[0]) < 4:
        date[0] = f'20{date[0]}'
    date = '-'.join(date)
    date = datetime.datetime.strptime(date, '%Y-%m-%d')

    # League
    name_list = match_result[1].split()
    league_dict = {
        'HSL': 'star_league',
        'HPL': 'pro_league',
        '종족최강전': 'event_league'
    }
    league_type = 'Unknown_League'
    index = -1
    for key, value in league_dict.items():
        index = name_list.index(key) if key in name_list else None
        if key == '종족최강전':
            index -= 1
        if index is not None:
            league_type = value
            break

    league_name = []
    if league_type != 'Unknown_League':
        for i in range(0, index + 2):
            if i < index:
                league_name.append(name_list[i])
            else:
                league_name.append(name_list[i].upper())
        league_name = ' '.join(league_name)
    else:
        league_name = 'Unknown League'


    # name
    name = ' '.join(name_list[index+2:])

    match_data_dict['date'] = date
    match_data_dict['league_name'] = league_name
    match_data_dict['league_type'] = league_type
    match_data_dict['name'] = name
    return match_data_dict
