from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback
import random
import json
import os

# СЮДА ВСТАВЬ СВОЙ ТОКЕН ОТ ГРУППЫ ВК
TOKEN = "vk1.a.vk1.a.13FDlqYTR1PjewPyc37RHas8POEvriWC5v-yDvx_TlIn-0WNthUoe5bn8g5I5UjLnKICAwqgP_hlYYx5rAgYWp2cUBQG4y48lvWMZosQ8LEZWBLMzOMEMrFE4c1UfRxd2DGitSda5GWrpFGP16UErog0E-eeK5IzhUi7GCnopuOSR0GdwnjbmpgfvP0HaRhRPRQJ545b-yIS960hP0R3Og"

bot = Bot(token=TOKEN)

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
@bot.on.message(text=["Начать", "начать", "/start"])
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
            f"С возвращением, {users[str(user_id)].get('name', 'путник')}!",
            keyboard=main_keyboard()
        )

# Профиль
@bot.on.message(text=["👤 Профиль", "!профиль", "/профиль"])
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
@bot.on.message(text=["💰 Работать", "!работать", "/работать"])
async def work_handler(message: Message):
    await message.answer(
        "💼 Выбери работу:\n\n"
        "⛏️ Шахтёр — 500₽ (тяжело)\n"
        "🚕 Таксист — 300₽ (средне)\n"
        "🍔 Повар — 200₽ (легко)",
        keyboard=work_inline_keyboard()
    )

# Обработка нажатий на инлайн-кнопки работы
@bot.on.raw_event("message_event", dataclass=message)
async def work_callback_handler(event):
    user_id = str(event.object.user_id)
    payload = event.object.payload
    
    if user_id not in users:
        register_user(int(user_id))
    
    user = users[user_id]
    
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
    
    action = payload.get("action")
    if action in rewards:
        reward = rewards[action]
        user['money'] += reward
        user['energy'] -= 10
        user['exp'] += random.randint(5, 15)
        
        # Повышение уровня
        if user['exp'] >= user['level'] * 100:
            user['level'] += 1
            user['exp'] = 0
            level_up_text = f"\n🎉 Поздравляю! Новый уровень: {user['level']}"
        else:
            level_up_text = ""
        
        save_db(users)
        
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=json.dumps({
                "type": "show_snackbar",
                "text": f"✅ Работа '{work_names[action]}' завершена! +{reward}₽"
            })
        )
        
        await bot.api.messages.send(
            user_id=event.object.user_id,
            random_id=0,
            message=f"💼 Ты поработал на должности '{work_names[action]}'\n"
                   f"💰 Заработано: +{reward}₽\n"
                   f"⚡ Энергия: {user['energy']}/100{level_up_text}"
        )

# Казино
@bot.on.message(text=["🎰 Казино", "!казино <amount>", "/казино <amount>"])
async def casino_handler(message: Message, amount=None):
    user_id = str(message.from_id)
    if user_id not in users:
        register_user(message.from_id)
    
    user = users[user_id]
    
    if not amount:
        await message.answer(
            f"🎰 Казино!\n\n"
            f"Используй: !казино [сумма]\n"
            f"Пример: !казино 100\n\n"
            f"💰 Твой баланс: {user['money']}₽"
        )
        return
    
    try:
        bet = int(amount)
    except:
        await message.answer("⚠️ Укажи корректную сумму!")
        return
    
    if bet > user['money']:
        await message.answer(f"⚠️ Недостаточно денег! У тебя {user['money']}₽")
        return
    
    if bet <= 0:
        await message.answer("⚠️ Сумма должна быть больше 0!")
        return
    
    # Игра
    win_chance = random.randint(1, 100)
    
    if win_chance <= 45:  # 45% шанс выигрыша
        win_amount = bet * 2
        user['money'] += bet
        result = f"🎉 Победа! +{bet}₽\n💰 Баланс: {user['money']}₽"
    else:
        user['money'] -= bet
        result = f"😢 Проигрыш! -{bet}₽\n💰 Баланс: {user['money']}₽"
    
    save_db(users)
    await message.answer(f"🎰 Казино\n\n{result}")

# Магазин
@bot.on.message(text=["🏪 Магазин", "!магазин", "/магазин"])
async def shop_handler(message: Message):
    await message.answer(
        "🏪 Магазин:\n\n"
        "⚔️ Меч — 500₽ (урон +20)\n"
        "🛡️ Щит — 300₽ (защита +15)\n"
        "💊 Аптечка — 100₽ (+50 HP)",
        keyboard=shop_inline_keyboard()
    )

# Обработка покупок
@bot.on.raw_event("message_event", dataclass=message)
async def shop_callback_handler(event):
    user_id = str(event.object.user_id)
    payload = event.object.payload
    
    if user_id not in users:
        register_user(int(user_id))
    
    user = users[user_id]
    
    items = {
        "buy_sword": {"name": "⚔️ Меч", "price": 500},
        "buy_shield": {"name": "🛡️ Щит", "price": 300},
        "buy_heal": {"name": "💊 Аптечка", "price": 100}
    }
    
    action = payload.get("action")
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
                message=f"🛒 Покупка завершена!\n"
                       f"{item['name']} добавлен в инвентарь\n"
                       f"💰 Баланс: {user['money']}₽"
            )
        else:
            await bot.api.messages.send_message_event_answer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps({
                    "type": "show_snackbar",
                    "text": f"⚠️ Недостаточно денег! Нужно {item['price']}₽"
                })
            )

# Инвентарь
@bot.on.message(text=["🎒 Инвентарь", "!инвентарь", "/инвентарь"])
async def inventory_handler(message: Message):
    user_id = str(message.from_id)
    if user_id not in users:
        register_user(message.from_id)
    
    user = users[user_id]
    if not user['inventory']:
        await message.answer("🎒 Твой инвентарь пуст!")
    else:
        items = "\n".join(user['inventory'])
        await message.answer(f"🎒 Твой инвентарь:\n\n{items}")

# Топ игроков
@bot.on.message(text=["📊 Топ", "!топ", "/топ"])
async def top_handler(message: Message):
    sorted_users = sorted(users.items(), key=lambda x: x[1]['money'], reverse=True)[:10]
    
    top_text = "🏆 Топ-10 богатейших игроков:\n\n"
    for i, (uid, data) in enumerate(sorted_users, 1):
        top_text += f"{i}. ID{uid} — {data['money']}₽\n"
    
    await message.answer(top_text)

# Запуск бота
if __name__ == "__main__":
    print("✅ Бот запущен!")
    bot.run_forever()