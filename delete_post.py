import telegram

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
