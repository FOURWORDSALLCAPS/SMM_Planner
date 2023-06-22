import asyncio
import time

from environs import Env
from upload_photo import upload_photo_to_album
from create_post import create_post_vk, create_post_tg
from delete_post import delete_post_vk, delete_post_tg
from get_link_post import get_link_post_vk, get_link_post_tg
from secondary_functions import get_documents, get_spreadsheet, download_photo, cut_url


async def main():
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
    text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
    url_google_docs = cut_url(text_sheet)
    text_publication = get_documents(credentials_file, url_google_docs)
    download_photo(text_sheet['values'][1][1])
    file_path = env('FILE_PATH')
    photo = await upload_photo_to_album(vk_token, vk_group_id, album_id, file_path)
    try:
        post_id = await create_post_vk(vk_token, vk_chat_id, text_publication, photo)
        message_id = await create_post_tg(tg_token, tg_chat_id, file_path, text_publication)
        # time.sleep(5)
        # await delete_post_vk(vk_token, vk_chat_id, post_id=post_id)
        # await delete_post_tg(tg_token, tg_chat_id, message_id=message_id)
        link_post_vk = get_link_post_vk(vk_group_id, post_id)
        link_post_tg = get_link_post_tg(tg_chat_id, message_id)
    except Exception as e:
        print(f'Произошла ошибка: {e}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
