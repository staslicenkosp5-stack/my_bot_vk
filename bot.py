from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback
from vkbottle.bot import BotLabeler
from vkbottle import GroupEventType, GroupTypes
import random
import json
import os

# СЮДА ВСТАВЬ СВОЙ ТОКЕН ОТ ГРУППЫ ВК
TOKEN = "vk1.a.13FDlqYTR1PjewPyc37RHas8POEvriWC5v-yDvx_TlIn-0WNthUoe5bn8g5I5UjLnKICAwqgP_hlYYx5rAgYWp2cUBQG4y48lvWMZosQ8LEZWBLMzOMEMrFE4c1UfRxd2DGitSda5GWrpFGP16UErog0E-eeK5IzhUi7GCnopuOSR0GdwnjbmpgfvP0HaRhRPRQJ545b-yIS960hP0R3Og"

bot = Bot(token=TOKEN)
labeler = BotLabeler()

# База данных (простой JSON файл)
DB_FILE = "users.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_db()

# Функция регистрации
def register_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "name": "",
            "money": 1000,
            "exp": 0,
            "level": 1,
            "hp": 100,
            "energy": 100,
            "inventory": [],
            "location": "Город"
        }
        save_db(users)
        return True
    return False

# Главная клавиатура с кнопками
def main_keyboard():
    kb = Keyboard(inline=False)
    kb.add(Text("👤 Профиль"), color=KeyboardButtonColor.PRIMARY)
    kb.add(Text("💰 Работать"), color=KeyboardButtonColor.POSITIVE)
    kb.row()
    kb.add(Text("🎰 Казино"), color=KeyboardButtonColor.NEGATIVE)
    kb.add(Text("🏪 Магазин"), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("🎒 Инвентарь"), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text("📊 Топ"), color=KeyboardButtonColor.PRIMARY)
    return kb.get_json()

# Инлайн-кнопки для работы
def work_inline_keyboard():
    kb = Keyboard(inline=True)
    kb.add(Callback("⛏️ Шахтёр (+500₽)", payload={"action": "work_miner"}))
    kb.row()
    kb.add(Callback("🚕 Таксист (+300₽)", payload={"action": "work_taxi"}))
    kb.row()
    kb.add(Callback("🍔 Повар (+200₽)", payload={"action": "work_cook"}))
    return kb.get_json()

# Инлайн-кнопки для магазина
def shop_inline_keyboard():
    kb = Keyboard(inline=True)
    kb.add(Callback("⚔️ Меч (500₽)", payload={"action": "buy_sword"}))
    kb.row()
    kb.add(Callback("🛡️ Щит (300₽)", payload={"action": "buy_shield"}))
    kb.row()
    kb.add(Callback("💊 Аптечка (100₽)", payload={"action": "buy_heal"}))
    return kb.get_json()

# Команда /start или "Начать"
@bot.on.message(text=["Начать", "начать", "/start", "привет", "Привет"])
async def start_handler(message: Message):
    user_id = message.from_id
    is_new = register_user(user_id)
    
    if is_new:
        await message.answer(
            f"🎮 Добро пожаловать в РП-мир!\n\n"
            f"Ты начинаешь свой путь в городе.\n"
            f"💰 Стартовый баланс: 1000₽\n"
            f"❤️ HP: 100\n"
            f"⚡ Энергия: 100\n\n"
            f"Используй кнопки ниже или команды:\n"
            f"!профиль, !работать, !казино, !магазин",
            keyboard=main_keyboard()
        )
    else:
        await message.answer(
            f"С возвращением в игру! Выбери действие:",
            keyboard=main_keyboard()
        )

# Профиль
@bot.on.message(text=["👤 Профиль", "!профиль", "/профиль", "профиль"])
async def profile_handler(message: Message):
    user_id = str(message.from_id)
    if user_id not in users:
        register_user(message.from_id)
    
    user = users[user_id]
    await message.answer(
        f"👤 Твой профиль:\n\n"
        f"💰 Деньги: {user['money']}₽\n"
        f"⭐ Уровень: {user['level']}\n"
        f"📊 Опыт: {user['exp']}\n"
        f"❤️ HP: {user['hp']}/100\n"
        f"⚡ Энергия: {user['energy']}/100\n"
        f"📍 Локация: {user['location']}"
    )

# Работать (с инлайн-кнопками)
@bot.on.message(text=["💰 Работать", "!работать", "/работать", "работать"])
async def work_handler(message: Message):
    await message.answer(
        "💼 Выбери работу:\n\n"
        "⛏️ Шахтёр — 500₽ (тяжело)\n"
        "🚕 Таксист — 300₽ (средне)\n"
        "🍔 Повар — 200₽ (легко)",
        keyboard=work_inline_keyboard()
    )

# Обработка нажатий на инлайн-кнопки (ИСПРАВЛЕННЫЙ ВАРИАНТ)
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, GroupTypes.MessageEvent)
async def callback_handler(event: GroupTypes.MessageEvent):
    user_id = str(event.object.user_id)
    payload = event.object.payload
    
    if user_id not in users:
        register_user(int(user_id))
    
    user = users[user_id]
    action = payload.get("action", "")
    
    # === РАБОТЫ ===
    if action.startswith("work_"):
        if user['energy'] < 10:
            await bot.api.messages.send_message_event_answer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps({"type": "show_snackbar", "text": "⚠️ Недостаточно энергии!"})
            )
            return
        
        rewards = {
            "work_miner": 500,
            "work_taxi": 300,
            "work_cook": 200
        }
        
        work_names = {
            "work_miner": "Шахтёр",
            "work_taxi": "Таксист",
            "work_cook": "Повар"
        }
        
        if action in rewards:
            reward = rewards[action]
            user['money'] += reward
            user['energy'] -= 10
            user['exp'] += random.randint(5, 15)
            
            # Повышение уровня
            level_up_text = ""
            if user['exp'] >= user['level'] * 100:
                user['level'] += 1
                user['exp'] = 0
                level_up_text = f"\n🎉 Новый уровень: {user['level']}"
            
            save_db(users)
            
            await bot.api.messages.send_message_event_answer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps({
                    "type": "show_snackbar",
                    "text": f"✅ +{reward}₽ за работу!"
                })
            )
            
            await bot.api.messages.send(
                user_id=event.object.user_id,
                random_id=0,
                message=f"💼 Работа: {work_names[action]}\n"
                       f"💰 +{reward}₽\n"
                       f"⚡ Энергия: {user['energy']}/100{level_up_text}",
                keyboard=main_keyboard()
            )
    
    # === МАГАЗИН ===
    elif action.startswith("buy_"):
        items = {
            "buy_sword": {"name": "⚔️ Меч", "price": 500},
            "buy_shield": {"name": "🛡️ Щит", "price": 300},
            "buy_heal": {"name": "💊 Аптечка", "price": 100}
        }
        
        if action in items:
            item = items[action]
            
            if user['money'] >= item['price']:
                user['money'] -= item['price']
                user['inventory'].append(item['name'])
                save_db(users)
                
                await bot.api.messages.send_message_event_answer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    event_data=json.dumps({
                        "type": "show_snackbar",
                        "text": f"✅ Куплено: {item['name']}"
                    })
                )
                
                await bot.api.messages.send(
                    user_id=event.object.user_id,
                    random_id=0,
                    message=f"🛒 Куплено: {item['name']}\n💰 Баланс: {user['money']}₽",
                    keyboard=main_keyboard()
                )
            else:
                await bot.api.messages.send_message_event_answer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    event_data=json.dumps({
                        "type": "show_snackbar",
                        "text": f"⚠️ Нужно {item['price']}₽"
                    })
                )

# Казино (текстовая команда с суммой)
@bot.on.message(text=["🎰 Казино", "!казино", "/казино", "казино"])
async def casino_info_handler(message: Message):
    user_id = str(message.from_id)
    if user_id not in users:
        register_user(message.from_id)
    
    user = users[user_id]
    await message.answer(
        f"🎰 Казино!\n\n"
        f"Напиши: !казино 100\n"
        f"(где 100 - твоя ставка)\n\n"
        f"💰 Твой баланс: {user['money']}₽"
    )

# Казино с суммой
@bot.on.message(text=["!казино <amount>", "/казино <amount>"])
async def casino_handler(message: Message, amount: str = None):
    user_id = str(message.from_id)
    if user_id not in users:
        register_user(message.from_id)
    
    user = users[user_id]
    
    try:
        bet = int(amount)
    except:
        await message.answer("⚠️ Укажи сумму! Пример: !казино 100")
        return
    
    if bet <= 0:
        await message.answer("⚠️ Сумма должна быть больше 0!")
        return
    
    if bet > user['money']:
        await message.answer(f"⚠️ У тебя только {user['money']}₽")
        return
    
    # Игра 45% шанс
    if random.randint(1, 100) <= 45:
        user['money'] += bet
        result = f"🎉 Победа! +{bet}₽"
    else:
        user['money'] -= bet
        result = f"😢 Проигрыш! -{bet}₽"
    
    save_db(users)
    await message.answer(f"🎰 {result}\n💰 Баланс: {user['money']}₽")

# Магазин
@bot.on.message(text=["🏪 Магазин", "!магазин", "/магазин", "магазин"])
async def shop_handler(message: Message):
    await message.answer(
        "🏪 Магазин:\n\n"
        "⚔️ Меч — 500₽\n"
        "🛡️ Щит — 300₽\n"
        "💊 Аптечка — 100₽",
        keyboard=shop_inline_keyboard()
    )

# Инвентарь
@bot.on.message(text=["🎒 Инвентарь", "!инвентарь", "/инвентарь", "инвентарь"])
async def inventory_handler(message: Message):
    user_id = str(message.from_id)
    if user_id not in users:
        register_user(message.from_id)
    
    user = users[user_id]
    if not user['inventory']:
        await message.answer("🎒 Инвентарь пуст!")
    else:
        items = "\n".join(user['inventory'])
        await message.answer(f"🎒 Инвентарь:\n\n{items}")

# Топ игроков
@bot.on.message(text=["📊 Топ", "!топ", "/топ", "топ"])
async def top_handler(message: Message):
    if not users:
        await message.answer("📊 Пока нет игроков!")
        return
    
    sorted_users = sorted(users.items(), key=lambda x: x[1]['money'], reverse=True)[:10]
    
    top_text = "🏆 Топ-10 богачей:\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        top_text += f"{i}. ID{uid} — {data['money']}₽\n"
    
    await message.answer(top_text)

# Запуск бота
if __name__ == "__main__":
    print("✅ Бот запущен!")
    bot.run_forever()
