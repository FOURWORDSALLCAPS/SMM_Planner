import gspread
import datetime
import asyncio
import time
import datetime
from environs import Env
from upload_photo import upload_photo_to_album
from create_post import create_post_vk, create_post_tg
from delete_post import delete_post_vk, delete_post_tg
from get_link_post import get_link_post_vk, get_link_post_tg
from secondary_functions import get_documents, get_spreadsheet, download_photo, get_url_photo, fill_cell, cut_url
from oauth2client.service_account import ServiceAccountCredentials


async def main():
    scope = ['https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/spreadsheets']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

    client = gspread.authorize(credentials)

    today = datetime.date.today()

    while True:
        sheet = client.open('SMMPlanner').sheet1
        data = sheet.get_all_values()
        headers = data[0]
        rows = data[1:]
        row_dict = {}
        for index, row in enumerate(rows):
            for idx, val in enumerate(row):
                header = headers[idx]
                row_dict[header] = val
            if row_dict.get('Дата постинга\nпубликации'):
                date_from_dict = datetime.datetime.strptime(row_dict['Дата постинга\nпубликации'], '%d.%m.%Y').date()
            else:
                date_from_dict = None
            if date_from_dict == today:
                try:
                    text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
                    url_google_docs = cut_url(text_sheet, index + 1)
                    text_publication = get_documents(credentials_file, url_google_docs)
                    download_photo(text_sheet, index + 1)
                    photo = await upload_photo_to_album(vk_token, vk_group_id, album_id, file_path)
                    post_id = await create_post_vk(vk_token, vk_chat_id, text_publication, photo)
                    link_post_vk = get_link_post_vk(vk_group_id, post_id)
                    fill_cell(credentials_file, spreadsheet_id, index + 2, link_post_vk)
                    time.sleep(0.5)
                except Exception as e:
                    print(f'Произошла ошибка: {e}')

        time.sleep(10)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    credentials_file = 'creds.json'
    spreadsheet_id = env('GOOGLE_EXEL_ID')
    vk_chat_id = env('VK_CHAT_ID')
    vk_group_id = env('VK_GROUP_ID')
    vk_token = env('VK_TOKEN')
    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    album_id = env('ALBUM_ID')
    file_path = env('FILE_PATH')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
