import telegram
import asyncio

from environs import Env
from get_google_docs import get_documents, get_spreadsheet, get_datetime, cut_url
from vkbottle import API


async def create_post_vk(vk_token, vk_chat_id, text_publication, datetime_publication):
    api = API(vk_token)
    await api.wall.post(owner_id=vk_chat_id, message=text_publication, publish_date=int(datetime_publication))


async def create_post_tg(bot_token, tg_chat_id, text_publication):
    bot = telegram.Bot(token=bot_token)
    await bot.send_message(chat_id=tg_chat_id, text=text_publication)


async def main():
    env = Env()
    env.read_env()
    credentials_file = 'creds.json'
    spreadsheet_id = env('GOOGLE_EXEL_ID')
    bot_token = env('TELEGRAM_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    vk_chat_id = env('VK_CHAT_ID')
    vk_token = env('VK_TOKEN')
    text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
    url_google_docs = cut_url(text_sheet)
    text_publication = get_documents(credentials_file, url_google_docs)
    datetime_publication = get_datetime(text_sheet)
    await create_post_tg(bot_token, tg_chat_id, text_publication)
    await create_post_vk(vk_token, vk_chat_id, text_publication, datetime_publication)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
