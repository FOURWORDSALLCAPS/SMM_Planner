import telegram
import asyncio

from environs import Env
from get_google_docs import get_documents, get_spreadsheet, cut_url


async def main():
    env = Env()
    env.read_env()
    credentials_file = 'creds.json'
    spreadsheet_id = env('GOOGLE_EXEL_ID')
    bot_token = env('TELEGRAM_TOKEN')
    chat_id = env('TG_CHAT_ID')
    bot = telegram.Bot(token=bot_token)
    text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
    url_google_docs = cut_url(text_sheet)
    text_doc = get_documents(credentials_file, url_google_docs)
    await bot.send_message(chat_id=chat_id, text=text_doc)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
