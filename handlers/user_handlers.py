from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart

from handlers.admin_handlers import AdminFilter
from admin_service import is_admin, get_admin_kb
from logger import log_event, logger

# Исправленный ID канала (добавьте -100 в начало)
CHANNEL_ID = -1002567330233  # Формат: -100 + фактический ID канала
router = Router()

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    try:
        if await is_admin(user_id):
            log_event(user_id, "ADMIN_START")
            await message.answer("👮‍♂️ Добро пожаловать в админ-панель",
                                reply_markup=get_admin_kb())
        else:
            log_event(user_id, "USER_START")
            await message.answer("Привет! \n \nЯ бот для вопросов.")
    except Exception as e:
        log_event(user_id, "START_ERROR", str(e))
        await message.answer("⚠ Произошла ошибка при обработке команды")

@router.message(~AdminFilter())
async def send_answer(message: Message, bot: Bot):
    user_id = message.from_user.id
    try:
        user_info = (
            f"👤 Пользователь: {message.from_user.full_name}\n"
            f"🆔 user_id: {user_id}\n"
            f"📧 Username: @{message.from_user.username}\n\n"
        )

        log_event(user_id, "MESSAGE_RECEIVED", f"Type: {message.content_type}")
        await message.answer("✅ Ваше сообщение было отправлено преподавателю. Скоро вам ответят в канале.")

        try:
            if message.text:
                log_event(user_id, "TEXT_SENT", f"Length: {len(message.text)} chars")
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=user_info + f"📝 Текст сообщения:\n\n{message.text}"
                )
            elif message.photo:
                log_event(user_id, "PHOTO_SENT")
                photo = message.photo[-1]
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo.file_id,
                    caption=user_info + (message.caption if message.caption else "📷 Пользователь отправил фото")
                )
            elif message.video:
                log_event(user_id, "VIDEO_SENT")
                await bot.send_video(
                    chat_id=CHANNEL_ID,
                    video=message.video.file_id,
                    caption=user_info + (message.caption if message.caption else "🎥 Пользователь отправил видео")
                )
            elif message.voice:
                log_event(user_id, "VOICE_SENT")
                await bot.send_voice(
                    chat_id=CHANNEL_ID,
                    voice=message.voice.file_id,
                    caption=user_info + "🎤 Голосовое сообщение от пользователя"
                )
            else:
                log_event(user_id, "UNSUPPORTED_TYPE", f"Type: {message.content_type}")
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=user_info + "⚠ Пользователь отправил неподдерживаемый тип сообщения"
                )
        except Exception as channel_error:
            log_event(user_id, "CHANNEL_SEND_ERROR", str(channel_error))
            await message.answer("⚠ Не удалось отправить сообщение в канал. Администратор уведомлён.")
            logger.error(f"Ошибка отправки в канал {CHANNEL_ID}: {channel_error}")

    except Exception as e:
        log_event(user_id, "SEND_ERROR", str(e))
        await message.answer("⚠ Произошла ошибка при отправке сообщения")