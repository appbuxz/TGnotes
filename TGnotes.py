import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

API_TOKEN = '7587174199:AAHWM0Bq3EgZtJMxU6wBvXMfmDBBLGRdrx8'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

reminders_file = 'reminders.json'

# Загрузка напоминаний из файла
def load_reminders():
    try:
        with open(reminders_file, 'r') as f:
            reminders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        reminders = {}
    return reminders

# Сохранение напоминаний в файл
def save_reminders(reminders):
    with open(reminders_file, 'w') as f:
        json.dump(reminders, f, indent=4)

# /start message
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("👋 Привет! Используй команду /help для списка команд.")

# /help command
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply(
        "/add - Добавить заметку 📝\n"
        "/list — показывает все твои напоминания 📋\n"
        "/remove <ID напоминания> — удаляет напоминание по ID ❌"
    )

# /add command
@dp.message(Command("add"))
async def cmd_add(message: types.Message):
    try:
        reminder_message = message.text.split(' ', 1)[1]  # Извлекаем текст напоминания после команды
    except IndexError:
        await message.reply("❗ Ошибка. Убедись, что ты указал текст напоминания.")
        return

    reminders = load_reminders()
    
    user_id = str(message.from_user.id)  # Используем строку для user_id
    if user_id not in reminders:
        reminders[user_id] = {"notes": {}}  # Если у пользователя нет напоминаний, создаем новый ключ

    note_id = len(reminders[user_id]["notes"]) + 1  # Генерация уникального ID для заметки
    reminders[user_id]["notes"][note_id] = reminder_message  # Добавляем новое напоминание
    
    save_reminders(reminders)  # Сохраняем изменения в файл
    await message.reply(f"✅ Напоминание '{reminder_message}' добавлено с ID {note_id}.")

# /list command
@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    reminders = load_reminders()
    user_id = str(message.from_user.id)
    
    if user_id in reminders and reminders[user_id]["notes"]:
        user_reminders = [f"{note_id}: {note}"
                          for note_id, note in reminders[user_id]["notes"].items()]
        await message.reply("📋 Твои напоминания:\n" + "\n".join(user_reminders))
    else:
        await message.reply("❌ У тебя нет напоминаний.")

# /remove command
@dp.message(Command("remove"))
async def cmd_remove(message: types.Message):
    try:
        # Получаем ID из текста команды и пытаемся преобразовать в строку
        reminder_id = str(message.text.split()[1])  # Преобразуем в строку
        reminders = load_reminders()

        # Проверяем, существует ли напоминание с таким ID и принадлежит ли оно текущему пользователю
        if reminder_id in reminders.get(str(message.from_user.id), {}).get('notes', {}):
            del reminders[str(message.from_user.id)]['notes'][reminder_id]  # Удаляем напоминание
            save_reminders(reminders)  # Сохраняем изменения
            await message.reply(f"❌ Напоминание с ID {reminder_id} удалено.")
        else:
            await message.reply("⚠️ Напоминание с таким ID не найдено.")
    except (IndexError, ValueError):
        await message.reply("❗ Ошибка. Убедись, что ты указал правильный ID.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
