import telegram
import asyncio
import tracemalloc
import time

from environs import Env
from get_google_docs import get_documents, get_spreadsheet, get_datetime, cut_url


async def create_post_tg(text_sheet, credentials_file):
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    url_google_docs = cut_url(text_sheet)
    text_publication = get_documents(credentials_file, url_google_docs)
    bot = telegram.Bot(token=tg_token)
    img = open(env('FILE_PATH'), 'rb')
    try:
        await bot.send_photo(chat_id=tg_chat_id, photo=img, caption=text_publication)
        print('Фото успешно отправлено')
    except Exception as e:
        print(f'Произошла ошибка при отправке фото: {e}')
    finally:
        img.close()


async def schedule_message():
    env = Env()
    env.read_env()
    credentials_file = 'creds.json'
    spreadsheet_id = env('GOOGLE_EXEL_ID')
    text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
    schedule_date = get_datetime(text_sheet)
    delay = int(schedule_date.timestamp() - time.time())
    await asyncio.sleep(delay)
    await create_post_tg(text_sheet, credentials_file)


if __name__ == '__main__':
    tracemalloc.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(schedule_message())
