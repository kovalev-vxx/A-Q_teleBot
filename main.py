from aiogram.utils import executor

from create_bot import dp
from handlers import client, admin
from utils import make_post
from aiogram.types import ContentType, Message

admin.register_handlers_admin(dp)
client.register_handlers_client(dp)
make_post.register_handlers_make_posts(dp)


@dp.message_handler(content_types=ContentType.ANY)
async def log(msg: Message):
    print(msg)


if __name__ == '__main__':
    executor.start_polling(dp)
