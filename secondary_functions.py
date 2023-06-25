import httplib2
import urllib.request
import hashlib
import time

from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
from urllib.parse import urlparse


def get_documents(credentials_file, document_id):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file,
        ['https://www.googleapis.com/auth/documents',
         'https://www.googleapis.com/auth/drive'])
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('docs', 'v1', http=http_auth)

    try:
        values = service.documents().get(documentId=document_id).execute()
    except HttpError as e:
        return e

    if values:
        doc_content = values.get('body').get('content')
        text = ''
        for content in doc_content:
            if 'paragraph' in content:
                elements = content['paragraph'].get('elements')
                for elem in elements:
                    text_run = elem.get('textRun')
                    if text_run:
                        text += text_run.get('content')

        return text


def get_spreadsheet(credentials_file, spreadsheet_id):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=http_auth)
    try:
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='A1:P10',
            majorDimension='ROWS',
        ).execute()
    except HttpError:
        values = None

    return values


def fill_cell(credentials_file, spreadsheet_id, cell_id, message):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credentials_file,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('sheets', 'v4', http=http_auth)
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"{cell_id}:{cell_id}",
                 "values": [[f"{message}"]]},
            ]
        }
    ).execute()


def cut_url(text_sheet, cell_id):
    url_bytes = text_sheet['values'][cell_id][0].encode('utf-8')
    url_parse = urlparse(url_bytes)
    path_parts = url_parse.path.split(b'/')
    doc_id = path_parts[3].replace(b'edit', b'')

    return doc_id.decode('utf-8')


def get_url_photo(text_sheet, cell_id):
    url_photo = text_sheet['values'][cell_id][1]

    return url_photo


def download_photo(text_sheet, cell_id):
    url = text_sheet['values'][cell_id][1]
    filename = "image.jpg"
    urllib.request.urlretrieve(url, "images/" + filename)


def create_sign(public_key, group_id, method, access_token, secret_key):
    timestamp = str(time.time())
    sign_str = f"application_key={public_key}ok_group_id={group_id}method={method}type=GROUP_THEMEformat=jsonmethod=" \
               f"{method}{timestamp}{access_token}{secret_key}"
    sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    return sign


def create_url(public_key, method, sign, access_token):
    url = f"https://api.ok.ru/fb.do?application_key={public_key}&method={method}&format=json&sig=" \
          f"{sign}&ok_access_token={access_token}"

    return url
