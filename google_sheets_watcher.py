import gspread
import asyncio
import time
import datetime
import logging

from environs import Env
from create_post import create_post_vk, create_post_tg, create_post_ok
from delete_post import delete_post_vk, delete_post_tg, delete_post_ok
from get_link_post import get_link_post_vk, get_link_post_tg, get_link_post_ok
from secondary_functions import get_documents, get_spreadsheet, download_photo, \
    fill_cell, cut_url,  upload_photo_ok, upload_photo_vk
from oauth2client.service_account import ServiceAccountCredentials


async def main():
    scope = ['https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/spreadsheets']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)

    client = gspread.authorize(credentials)

    vk_posts_ids_to_delete = []

    tg_posts_ids_to_delete = []

    ok_posts_ids_to_delete = []

    while True:
        sheet = client.open('SMMPlanner').sheet1
        data = sheet.get_all_values()
        headers = data[0]
        rows = data[1:]
        row_dict = {}
        today = datetime.date.today()
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        for index, row in enumerate(rows):
            for idx, val in enumerate(row):
                header = headers[idx]
                row_dict[header] = val
            try:
                if row_dict.get('Дата постинга\nпубликации'):
                    date_publication = datetime.datetime.strptime(row_dict['Дата постинга\nпубликации'], '%d.%m.%Y') \
                        .date()
                else:
                    date_publication = None
                if row_dict.get('Дата удаления\nпубликации'):
                    date_delete_publication = datetime.datetime.strptime(row_dict['Дата удаления\nпубликации'],
                                                                         '%d.%m.%Y').date()
                else:
                    date_delete_publication = None
                if row_dict.get('Время постинга\nпубликации'):
                    time_publication = datetime.datetime.strptime(row_dict['Время постинга\nпубликации'], '%H:%M') \
                        .strftime('%H:%M')
                else:
                    time_publication = None
                if row_dict.get('Время удаления\nпубликации'):
                    time_delete_publication = datetime.datetime.strptime(row_dict['Время удаления\nпубликации'],
                                                                         '%H:%M').strftime('%H:%M')
                else:
                    time_delete_publication = None
                if date_publication == today:
                    if time_publication == current_time:
                        try:
                            text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
                            url_google_docs = cut_url(text_sheet, index + 1)
                            text_publication = get_documents(credentials_file, url_google_docs)
                            download_photo(text_sheet, index + 1)
                            if row_dict.get('Соц. сеть\nVK') == 'Да' and not row_dict.get('Статус публикации\nVk'):
                                photo = await upload_photo_vk(vk_token, vk_group_id, album_id, file_path)
                                post_id = await create_post_vk(vk_token, vk_chat_id, text_publication, photo)
                                link_post_vk = get_link_post_vk(vk_group_id, post_id)
                                fill_cell(credentials_file, spreadsheet_id, f'N{index + 2}', link_post_vk)
                                fill_cell(credentials_file, spreadsheet_id, f'Q{index + 2}', 'Да')
                                if date_delete_publication >= today:
                                    vk_posts_ids_to_delete.append(post_id)
                                print('Создание поста в Vk прошло успешно!')
                            elif row_dict.get('Соц. сеть\nTelegram') == 'Да' \
                                    and not row_dict.get('Статус публикации\nTg'):
                                message_id = await create_post_tg(tg_token, tg_chat_id, file_path, text_publication)
                                link_post_tg = get_link_post_tg(tg_chat_id, message_id)
                                fill_cell(credentials_file, spreadsheet_id, f'O{index + 2}', link_post_tg)
                                fill_cell(credentials_file, spreadsheet_id, f'R{index + 2}', 'Да')
                                if date_delete_publication >= today:
                                    tg_posts_ids_to_delete.append(message_id)
                                print('Создание поста в Telegram прошло успешно!')
                            elif row_dict.get('Соц. сеть\nOK') == 'Да' and not row_dict.get('Статус публикации\nOK'):
                                photo_attachment = upload_photo_ok(ok_public_key, ok_group_id, ok_access_token, ok_secret_key)
                                post_id = create_post_ok(ok_group_id, text_publication, ok_public_key,
                                                         ok_access_token, photo_attachment, ok_secret_key)
                                link_post_ok = get_link_post_ok(ok_group_id, post_id)
                                fill_cell(credentials_file, spreadsheet_id, f'P{index + 2}', link_post_ok)
                                fill_cell(credentials_file, spreadsheet_id, f'S{index + 2}', 'Да')
                                if date_delete_publication >= today:
                                    ok_posts_ids_to_delete.append(post_id)
                                print('Создание поста в OK прошло успешно!')

                            time.sleep(0.5)
                        except Exception as e:
                            if isinstance(e, IndexError) and str(e) == 'list index out of range':
                                fill_cell(credentials_file, spreadsheet_id, f'M{index + 2}', 'unknown document url')
                            else:
                                fill_cell(credentials_file, spreadsheet_id, f'M{index + 2}', f'{e}')
                if date_delete_publication == today:
                    if time_delete_publication == current_time:
                        try:
                            if vk_posts_ids_to_delete:
                                for post_id in vk_posts_ids_to_delete:
                                    await delete_post_vk(vk_token, vk_chat_id, post_id)
                                print('Удаление поста в Vk прошло успешно!')
                            if tg_posts_ids_to_delete:
                                for message_id in tg_posts_ids_to_delete:
                                    await delete_post_tg(tg_token, tg_chat_id, message_id)
                                print('Удаление поста в Telegram прошло успешно!')
                            if ok_posts_ids_to_delete:
                                for post_id in ok_posts_ids_to_delete:
                                    delete_post_ok(ok_group_id, ok_access_token, post_id, ok_public_key, ok_secret_key)
                                print('Удаление поста в OK прошло успешно!')
                        except Exception as e:
                            fill_cell(credentials_file, spreadsheet_id, f'M{index + 2}', f'{e}')
            except Exception as e:
                fill_cell(credentials_file, spreadsheet_id, f'M{index + 2}', f'{e}')
        time.sleep(10)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
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
    ok_public_key = env('OK_PUBLIC_KEY')
    ok_secret_key = env('OK_SECRET_KEY')
    ok_access_token = env('OK_TOKEN')
    ok_group_id = env('OK_GROUP_ID')
    file_path = env('FILE_PATH')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
