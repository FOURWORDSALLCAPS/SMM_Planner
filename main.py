import asyncio

from environs import Env
from get_google_docs import get_documents, get_spreadsheet, get_datetime, cut_url
from upload_photo import upload_photo_to_album
from vkbottle import API


async def create_post_vk(token, chat_id, text_publication, datetime_publication, photo):
    api = API(token)
    await api.wall.post(owner_id=chat_id,
                        publish_date=int(datetime_publication),
                        attachments=photo,
                        message=text_publication)


async def main():
    env = Env()
    env.read_env()
    credentials_file = 'creds.json'
    spreadsheet_id = env('GOOGLE_EXEL_ID')
    vk_chat_id = env('VK_CHAT_ID')
    vk_group_id = env('VK_GROUP_ID')
    vk_token = env('VK_TOKEN')
    album_id = env('ALBUM_ID')
    file_path = env('FILE_PATH')
    text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
    url_google_docs = cut_url(text_sheet)
    text_publication = get_documents(credentials_file, url_google_docs)
    datetime_publication = get_datetime(text_sheet)
    photo = await upload_photo_to_album(vk_token, vk_group_id, album_id, file_path)
    await create_post_vk(vk_token, vk_chat_id, text_publication, datetime_publication, photo)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
