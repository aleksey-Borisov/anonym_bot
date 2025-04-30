from aiogram.utils.keyboard import InlineKeyboardBuilder


ADMIN_IDS = [1124279101]
# 1124279100
async def is_admin(user_id: int):
  return user_id in ADMIN_IDS


def get_admin_kb():
  builder = InlineKeyboardBuilder()
  builder.button(text=" Список забаненных", callback_data="banned_list")
  builder.button(text=" Забанить пользователся", callback_data="ban_user")
  builder.button(text=" Разбанить пользователся", callback_data="unban_user")
  builder.adjust(1)
  return builder.as_markup()


