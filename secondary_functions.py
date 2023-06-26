import httplib2
import urllib.request
import hashlib
import time
import requests

from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
from urllib.parse import urlparse
from vkbottle import API, VKAPIError


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


def upload_photo_ok(public_key, group_id, access_token, secret_key):
    method = 'photosV2.getUploadUrl'
    sign = create_sign(public_key, group_id, method, access_token, secret_key)
    url = create_url(public_key, method, sign, access_token)

    response = requests.post(url, data={'gid': group_id, 'count': 1, 'access_token': access_token})
    response.raise_for_status()
    if not response.ok:
        return None
    upload_url = response.json()['upload_url']

    files = {"file": ("image.jpeg", open("images/image.jpeg", "rb"), 'image/jpeg')}
    upload_response = requests.post(upload_url, files=files)

    photo_keys = list(upload_response.json()['photos'].keys())
    photo_data = upload_response.json()['photos'][photo_keys[0]]

    photo_token = photo_data.get("token")

    photo_attachment = {'type': 'photo', 'list': [{"id": photo_token}]}

    return photo_attachment


async def upload_photo_vk(token, group_id, album_id, file_path):
    try:
        api = API(token)
        upload_url = await api.photos.get_upload_server(group_id=group_id, album_id=album_id)
        response = requests.post(upload_url.upload_url, files={'photo': open(file_path, 'rb')})
        response.raise_for_status()
        if not response.ok:
            return None
        result_upload = response.json()
        photos_list = result_upload['photos_list']
        server = result_upload['server']
        hash_value = result_upload['hash']
        photo_info = await api.photos.save(album_id=album_id,
                                           group_id=group_id,
                                           server=server,
                                           hash=hash_value,
                                           photos_list=photos_list)
        attachment = f"photo{photo_info[0].owner_id}_{photo_info[0].id}"
        return attachment
    except VKAPIError as e:
        print(f"VK API error occurred: {e}")
        return None


def download_photo(text_sheet, cell_id):
    url = text_sheet['values'][cell_id][1]
    filename = "image.jpeg"
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
