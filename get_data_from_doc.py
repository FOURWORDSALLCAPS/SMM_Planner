from pprint import pprint
from environs import Env
import httplib2
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError

env = Env()
env.read_env()

CREDENTIALS_FILE = 'creds.json'
document_id = env('GOOGLE_DOCS_ID')

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/documents',
     'https://www.googleapis.com/auth/drive'])
http_auth = credentials.authorize(httplib2.Http())
docs_service = discovery.build('docs', 'v1', http=http_auth)

try:
    doc = docs_service.documents().get(documentId=document_id).execute()
except HttpError as error:
    print(f'An error occurred: {error}')
    doc = None

if doc:
    doc_content = doc.get('body').get('content')
    text = ''
    for content in doc_content:
        if 'paragraph' in content:
            elements = content['paragraph'].get('elements')
            for elem in elements:
                text_run = elem.get('textRun')
                if text_run:
                    text += text_run.get('content')
    print(text)
else:
    print('Документ не найден или произошла ошибка при получении его содержимого')
