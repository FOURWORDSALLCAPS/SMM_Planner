import telegram
import requests
import json

from vkbottle import API


async def create_post_tg(token, chat_id, img, text_publication):
    bot = telegram.Bot(token=token)
    try:
        message = await bot.send_photo(chat_id=chat_id,
                                       photo=img,
                                       caption=text_publication)
        post_id = message.message_id
        return post_id
    except Exception as e:
        print(f'Произошла ошибка при создании поста: {e}')


async def create_post_vk(token, chat_id, text_publication, photo):
    api = API(token)
    try:
        post_data = await api.wall.post(owner_id=chat_id,
                                        attachments=photo,
                                        message=text_publication)
        post_id = post_data.post_id
        return post_id
    except Exception as e:
        print(f'Произошла ошибка при создании поста: {e}')


def create_post_ok(group_id, text_publication, url, access_token):
    attachment = {
        'media': [
            {
                'type': 'text',
                'text': text_publication
            }
        ]
    }

    response = requests.post(url, data={'gid': group_id, 'type': 'GROUP_THEME', 'access_token': access_token,
                                        'attachment': json.dumps(attachment)})

    try:
        response.raise_for_status()
    except Exception as e:
        print(e)

    ok_post_id = response.json()

    return ok_post_id
