import sqlite3
from aiogram import Router, F, Bot
from aiogram.filters import Command, Filter
from aiogram.types import Message, CallbackQuery
import logger
from admin_service import is_admin

router = Router()

class AdminFilter(Filter):
  async def __call__(self, message: Message) -> bool:
    return await is_admin(message.from_user.id)


@router.message(Command("ban"), AdminFilter())
async def ban_user(message: Message, bot: Bot):
  args = message.text.split()
  if len(args) < 3:
    return await message.answer(
      "Введите в корректном формате.\n\nℹ️ Формат: /ban `<user_id>` `<причина>`",
      parse_mode="MarkdownV2"
    )

  try:
    user_id = int(args[1])
    reason = ' '.join(args[2:])

    try:
      user = await bot.get_chat(user_id)
    except:
      return await message.answer("❌ Пользователь не найден")

    with sqlite3.connect('bans.db') as conn:
      cursor = conn.cursor()

      if cursor.execute("SELECT 1 FROM banned_users WHERE user_id=?", (user_id,)).fetchone():
        return await message.answer("⚠️ Этот пользователь уже забанен")

      cursor.execute('''INSERT INTO banned_users 
                            (user_id, username, reason) 
                            VALUES (?, ?, ?)''',
                     (user_id, user.username, reason))
      conn.commit()

    await message.answer(f"✅ Пользователь {user.username or user_id} забанен.\nПричина: {reason}")
    logger.info(f"Admin {message.from_user.id} banned {user_id}. Reason: {reason}")

  except ValueError:
    await message.answer("❌ ID пользователя должен быть числом")
  except Exception as e:
    await message.answer(f"⚠️ Ошибка: {str(e)}")
    logger.error(f"Ban error: {str(e)}")
@router.message(Command("unban"), AdminFilter())
async def unban_user(message: Message):
    args = message.text.split()
    if len(args) < 2:
      return await message.answer(
        "ℹ️ Формат: /ban `<user_id>` `<причина>`",
        parse_mode="MarkdownV2"
      )

    try:
        user_id = int(args[1])

        conn = sqlite3.connect('bans.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM banned_users WHERE user_id=?", (user_id,))

        if not cursor.fetchone():
            conn.close()
            return await message.answer("⚠ Этот пользователь не забанен")

        cursor.execute("DELETE FROM banned_users WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()

        await message.answer(f"✅ Пользователь {user_id} разбанен")

    except ValueError:
        await message.answer("❌ Неверный формат ID пользователя")
    except Exception as e:
        await message.answer(f"⚠ Ошибка при разбане пользователя: {str(e)}")



@router.callback_query(F.data == "banned_list", AdminFilter())
async def banned_list(callback: CallbackQuery):

  conn = sqlite3.connect('bans.db')
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM banned_users")
  banned_users = cursor.fetchall()
  conn.close()

  if not banned_users:
    return await callback.message.answer("🚫 Нет забаненных пользователей")

  response = "📋 Список забаненных пользователей:\n\n"
  for user in banned_users:
    response += f"🆔 : {user[0]}\n Причина: {user[2]}\n\n"

  await callback.message.answer(response)
  await callback.answer()


@router.callback_query(F.data == "ban_user", AdminFilter())
async def ban_user_instructions(callback: CallbackQuery):
    """Инструкции по бану"""
    await callback.message.answer(
        "📝 Для бана пользователя введите:\n"
        "<code>/ban user_id причина</code>\n\n"
        "Пример:\n"
        "<code>/ban 12345678 Нарушение правил</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "unban_user", AdminFilter())
async def ban_user_instructions(callback: CallbackQuery):
    """Инструкции по бану"""
    await callback.message.answer(
        "📝 Для разбана пользователя введите:\n"
        "<code>/unban user_id</code>\n\n"
        "Пример:\n"
        "<code>/unban 12345678</code>",
        parse_mode="HTML"
    )
    await callback.answer()