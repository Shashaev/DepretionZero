import asyncio

import aiogram

import settings
import router
import commands


bot = aiogram.Bot(token=settings.TOKEN)
dp = aiogram.Dispatcher()


async def main() -> None:
    dp.include_router(router.router)
    await bot.set_my_commands(commands.commands)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
