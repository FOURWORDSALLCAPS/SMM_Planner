import asyncio

from vkbottle import API
from environs import Env
from get_google_docs import get_documents, get_spreadsheet, cut_url


async def main():
    env = Env()
    env.read_env()
    vk_token = env('VK_TOKEN')
    api = API(vk_token)
    owner_id = env('VK_USER_ID')
    credentials_file = 'creds.json'
    spreadsheet_id = env('GOOGLE_EXEL_ID')
    text_sheet = get_spreadsheet(credentials_file, spreadsheet_id)
    url_google_docs = cut_url(text_sheet)
    text_doc = get_documents(credentials_file, url_google_docs)
    await api.wall.post(owner_id=owner_id, friends_only=True, message=text_doc)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
