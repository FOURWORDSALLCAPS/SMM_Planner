import httplib2

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
    except HttpError:
        values = None

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
            range='A1:E10',
            majorDimension='ROWS',
        ).execute()
    except HttpError:
        values = None

    return values


def cut_url(text_sheet):
    url_bytes = text_sheet['values'][1][0].encode('utf-8')
    url_parse = urlparse(url_bytes)
    path_parts = url_parse.path.split(b'/')
    doc_id = path_parts[3].replace(b'edit', b'')

    return doc_id.decode('utf-8')
