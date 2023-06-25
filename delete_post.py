import telegram
import requests

from secondary_functions import create_url, create_sign

from vkbottle import API


async def delete_post_tg(token, chat_id, message_id):
    bot = telegram.Bot(token=token)
    try:
        await bot.deleteMessage(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f'Произошла ошибка при удалении поста: {e}')


async def delete_post_vk(token, chat_id, post_id):
    api = API(token)
    try:
        await api.wall.delete(owner_id=chat_id, post_id=post_id)
    except Exception as e:
        print(f'Произошла ошибка при удалении поста: {e}')


def delete_post_ok(group_id, access_token, post_id, public_key, secret_key):
    method = 'mediatopic.deleteTopic'

    sign = create_sign(public_key, group_id, method, access_token, secret_key)
    url = create_url(public_key, method, sign, access_token)
    response = requests.post(url, data={'gid': group_id, 'topic_id': post_id, 'access_token': access_token})
    try:
        response.raise_for_status()
    except Exception as e:
        print(f'Произошла ошибка при удалении поста: {e}')
