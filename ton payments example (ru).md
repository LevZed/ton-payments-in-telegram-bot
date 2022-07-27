# ton footstep 8 (ru)

by [@Revuza](https://t.me/revuza)

    
---

# Приём платежей в TON с использованием telegram бота

---


## Начало

У нас есть возможность взаимодействовать с блокчейном используя сторонние api предоставляемые некоторыми участниками сети. Благодаря этим сервисам разработчики могут пропустить шаг с запуском собственной ноды и настройкой своего api.

В данной статье будет описан процесс создания телеграм бота, способного верифицировать платежи в сети ТОН используя стороннее api предоставляемое TON Center.

Мы будем создавать бота используя библиотеку для python - aiogram. в качестве тестовой базы данных будет использован Sqlite. В дополнении к статье я покажу, как настроить heroku postgres. Бот будет деплоится из репозитория на платформу heroku.

Я использую VS code.

## Telegram бот

Для начала создадим основу для бота.

Создадим три файла:

`main.py`

`api.py`

`db.py`

Начало `main.py`:

```python
# Импортируем модули из aiogram необходимые для нашего бота
import logging
from aiogram import Bot, Dispatcher, executor, types
# MemoryStorage нужен для временного хранения информации
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# FSM для разбития процесса оплаты на отдельные шаги
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import json

# А так же наши модули в которых будет код 
# для взаимодействия с API и базой данных
import db
import api
```

Для удобства предлагаю хранить данные такие как `BOT_TOKEN` или ваш кошелёк для приёма платежей в отдельном файле `config.json`:

```json
{
    "BOT_TOKEN": "Your bot token",
    "MAINNET_API_TOKEN": "Your mainnet api token",
    "TESTNET_API_TOKEN": "Your testnet api token",
    "MAINNET_WALLET": "Your mainnet wallet",
    "TESTNET_WALLET": "Your testnet wallet",
    "WORK_MODE": "testnet"
}
```

В ключе `WORK_MODE` мы будем определять режим работы бота - в тестовой или основной сети: `testnet` или `mainnet` соответственно.

Api токен для `*_API_TOKEN` можно получить в боте [toncenter](https://toncenter.com/):

для mainnet - [@tonapibot](https://t.me/tonapibot)

для testnet - [@tontestnetapibot](https://t.me/tontestnetapibot)

Далее, чтобы получить токен для работы бота, мы читаем его из файла `config.json`:

```python
with open('config.json', 'r') as f:
    config_json = json.load(f)
    BOT_TOKEN = config_json['BOT_TOKEN']
		# нам нужно знать, какой кошелёк будет принимать платежы
    MAINNET_WALLET = config_json['MAINNET_WALLET']
    TESTNET_WALLET = config_json['TESTNET_WALLET']
    WORK_MODE = config_json['WORK_MODE']

if WORK_MODE == "mainnet":
    WALLET = MAINNET_WALLET
else:
		# По умолчанию бот будет работать в тестовой сети
    WALLET = TESTNET_WALLET
```

Далее мы заканчиваем настройку бота:

```python
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

class DataInput (StatesGroup):
    firstState = State()
    secondState = State()
    WalletState = State()
    PayState = State()
```

В конце не забываем про:

```python
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
```

Этот блок находится в самом конце файла, после всех обработчиков.

Не буду уходить ещё глубже. За подробностями и примерами предлагаю заглянуть в [документацию Aiogram](https://docs.aiogram.dev/en/latest/).

### Полный код `main.py`.

```python
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import json

import db
import api

with open('config.json', 'r') as f:
    config_json = json.load(f)
    BOT_TOKEN = config_json['BOT_TOKEN']
    MAINNET_WALLET = config_json['MAINNET_WALLET']
    TESTNET_WALLET = config_json['TESTNET_WALLET']
    WORK_MODE = config_json['WORK_MODE']

if WORK_MODE == "mainnet":
    WALLET = MAINNET_WALLET
else:
    WALLET = TESTNET_WALLET

# Configure logging
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
# storage=MemoryStorage() needed for FSM
dp = Dispatcher(bot, storage=MemoryStorage())

class DataInput (StatesGroup):
    firstState = State()
    secondState = State()
    WalletState = State()
    PayState = State()

# /start command handler
@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message):
    await message.answer(f"WORKMODE: {WORK_MODE}")
    # check if user is in database. if not, add him
    isOld = db.check_user(
        message.from_user.id, message.from_user.username, message.from_user.first_name)
    # if user already in database, we can address him differently
    if isOld == False:
        await message.answer(f"You are new here, {message.from_user.first_name}!")
        await message.answer(f"to buy air send /buy")
    else:
        await message.answer(f"Welcome once again, {message.from_user.first_name}!")
        await message.answer(f"to buy more air send /buy")
    await DataInput.firstState.set()

@dp.message_handler(commands=['cancel'], state="*")
async def cmd_cancel(message: types.Message):
    await message.answer("Canceled")
    await message.answer("/start to restart")
    await DataInput.firstState.set()

@dp.message_handler(commands=['buy'], state=DataInput.firstState)
async def cmd_buy(message: types.Message):
    # reply keyboard with air types
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton('Just pure 🌫'))
    keyboard.add(types.KeyboardButton('Spring forest 🌲'))
    keyboard.add(types.KeyboardButton('Sea breeze 🌊'))
    keyboard.add(types.KeyboardButton('Fresh asphalt 🛣'))
    await message.answer(f"Choose your air: (or /cancel)", reply_markup=keyboard)
    await DataInput.secondState.set()

@dp.message_handler(commands=['me'], state="*")
async def cmd_me(message: types.Message):
    await message.answer(f"Your transactions")
    # db.get_user_payments returns list of transactions for user
    transactions = db.get_user_payments(message.from_user.id)
    if transactions == False:
        await message.answer(f"You have no transactions")
    else:
        for transaction in transactions:
            # we need to remember that blockchain stores value in nanotons. 1 toncoin = 1000000000 in blockchain
            await message.answer(f"{int(transaction['value'])/1000000000} - {transaction['comment']}")

# handle air type
@dp.message_handler(state=DataInput.secondState)
async def air_type(message: types.Message, state: FSMContext):
    if message.text == "Just pure 🌫":
        await state.update_data(air_type="Just pure 🌫")
        await DataInput.WalletState.set()
    elif message.text == "Fresh asphalt 🛣":
        await state.update_data(air_type="Fresh asphalt 🛣")
        await DataInput.WalletState.set()
    elif message.text == "Spring forest 🌲":
        await state.update_data(air_type="Spring forest 🌲")
        await DataInput.WalletState.set()
    elif message.text == "Sea breeze 🌊":
        await state.update_data(air_type="Sea breeze 🌊")
        await DataInput.WalletState.set()
    else:
        await message.answer("Wrong air type")
        await DataInput.secondState.set()
        return
    await message.answer(f"Send your wallet address")

# handle wallet address

@dp.message_handler(state=DataInput.WalletState)
async def user_wallet(message: types.Message, state: FSMContext):
    if len(message.text) == 48:
        res = api.detect_address(message.text)
        if res == False:
            await message.answer("Wrong wallet address")
            await DataInput.WalletState.set()
            return
        else:
            user_data = await state.get_data()
            air_type = user_data['air_type']
            # inline button "check transaction"
            keyboard2 = types.InlineKeyboardMarkup(row_width=1)
            keyboard2.add(types.InlineKeyboardButton(
                text="Check transaction", callback_data="check"))
            keyboard1 = types.InlineKeyboardMarkup(row_width=1)
            keyboard1.add(types.InlineKeyboardButton(
                text="Ton Wallet", url=f"ton://transfer/{WALLET}?amount=1000000000&text={air_type}"))
            keyboard1.add(types.InlineKeyboardButton(
                text="Tonkeeper", url=f"https://app.tonkeeper.com/transfer/{WALLET}?amount=1000000000&text={air_type}"))
            keyboard1.add(types.InlineKeyboardButton(
                text="Tonhub", url=f"https://tonhub.com/transfer/{WALLET}?amount=1000000000&text={air_type}"))
            await message.answer(f"You choose {air_type}")
            await message.answer(f"Send <code>1</code> toncoin to address \n<code>{WALLET}</code> \nwith comment \n<code>{air_type}</code> \nfrom your wallet ({message.text}) \nton://transfer/{WALLET}?amount=1000000000&text={air_type}", reply_markup=keyboard1)
            await message.answer(f"Click the button after payment", reply_markup=keyboard2)
            await DataInput.PayState.set()
            await state.update_data(wallet=res)
            await state.update_data(value_nano="1000000000")
    else:
        await message.answer("Wrong wallet address")
        await DataInput.WalletState.set()

@dp.callback_query_handler(lambda call: call.data == "check", state=DataInput.PayState)
async def check_transaction(call: types.CallbackQuery, state: FSMContext):
    # send notification
    user_data = await state.get_data()
    source = user_data['wallet']
    value = user_data['value_nano']
    comment = user_data['air_type']
    result = api.find_transaction(source, value, comment)
    if result == False:
        await call.answer("Wait a bit, try again in 10 seconds. You can also check the status of the transaction through the explorer (ton.sh/)", show_alert=True)
    else:
        db.v_wallet(call.from_user.id, source)
        await call.message.edit_text("Transaction is confirmed \n/start to restart")
        await state.finish()
        await DataInput.firstState.set()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
```

*Подробности по некоторым моментам смотрите в комментариях к коду.*

## База данных

### Создаём БД

В данном примере используется локальная база данных Sqlite.

У нас есть 2 таблицы:

transactions

```sql
CREATE TABLE transactions (
    source  VARCHAR (48) NOT NULL,
    hash    VARCHAR (50) UNIQUE
                         NOT NULL,
    value   INTEGER      NOT NULL,
    comment VARCHAR (50) 
);
```

![Untitled](ton%20footstep%208%20(ru)%2089efbd0580e045958611562e2623ab1e/Untitled.png)

users

```sql
CREATE TABLE users (
    id         INTEGER       UNIQUE
                             NOT NULL,
    username   VARCHAR (33),
    first_name VARCHAR (300),
    wallet     VARCHAR (50)  DEFAULT none
);
```

![Untitled](ton%20footstep%208%20(ru)%2089efbd0580e045958611562e2623ab1e/Untitled%201.png)

В таблице `users` мы храним … пользователей. Их telegram id, @username, first name и кошелёк. Кошелёк добавляется в базу данных при первой успешной оплате.

В таблице `transactions` хранятся верифицированные транзакции.

### Работаем с БД

Открываем `db.py`.

Пользователь сделал транзакцию и нажал на кнопку для её проверки. Как сделать так, чтобы одну и туже транзакцию, он не подтвердил дважды?

В транзакциях присутствует body_hash, при помощи которого мы можем легко понять - есть транзакция в бд или нет.

В базу данных мы добавляем транзакции, в которых мы “уверены”. А функция `check_transaction` проверяет есть ли найденная транзакция в базе или нет.

```python
def add_v_transaction(source, hash, value, comment):
    cur.execute("INSERT INTO transactions (source, hash, value, comment) VALUES (?, ?, ?, ?)",
                (source, hash, value, comment))
    locCon.commit()
```

```python
def check_transaction(hash):
    cur.execute(f"SELECT hash FROM transactions WHERE hash = '{hash}'")
    result = cur.fetchone()
    if result:
        return True
    return False
```

`get_user_payments` возвращает список покупок пользователя.

```python
def get_user_payments(user_id):
    wallet = get_user_wallet(user_id)

    if wallet == "none":
        return "You have no wallet"
    else:

        cur.execute(f"SELECT * FROM transactions WHERE source = '{wallet}'")
        result = cur.fetchall()
        tdict = {}
        tlist = []
        try:
            for transaction in result:
                tdict = {
                    "value": transaction[2],
                    "comment": transaction[3],
                }
                tlist.append(tdict)
            return tlist

        except:

            return False
```

## API

### Необходимые запросы

По сути, что нам нужно, чтобы подтвердить, что пользователь перевёл нам нужную сумму? Нам просто нужно посмотреть последние входящие переводы на наш кошелёк и среди них найти транзакцию с нужного адреса, с нужной суммой (и возможно уникальным комментарием). Для всего этого у toncenter есть метод `getTransactions`:

![Untitled](ton%20footstep%208%20(ru)%2089efbd0580e045958611562e2623ab1e/Untitled%202.png)

Применив его, по умолчанию, мы получим последние 10 транзакций. Однако мы можем так же указать, что нам нужно получить больше. Однако, чем больше вы запрашиваете, тем дольше будет ответ. Да и, скорее всего, не нужно вам столько. Если вы хотите получить большее количество, то у каждой транзакции есть `lt` и `hash` . Вы можете посмотреть, например, 30 транзакций и если среди них не нашлась нужная, тогда взять `lt` и `hash` из последней и добавить их к запросу - получив следующие 30 транзакций и так далее.

Для примера - есть кошелёк в тестовой сети `EQAVKMzqtrvNB2SkcBONOijadqFZ1gMdjmzh1Y3HB1p_zai5`, у него всего 4 транзакции:

Использовав запрос `https://testnet.toncenter.com/api/v2/getTransactions?address=EQAVKMzqtrvNB2SkcBONOijadqFZ1gMdjmzh1Y3HB1p_zai5&limit=2&to_lt=0&archival=true` мы получим следующий ответ:

```json
{
  "ok": true,
  "result": [
    {
      "@type": "raw.transaction",
      "utime": 1658130319,
      "data": "te6cckECBQEAAR4AA7FxUozOq2u80HZKRwE406KNp2oVnWAx2ObOHVjccHWn/NAAABxMCR0wOHEhCqfuVgP9z981Ltb+JWyDaTHSn+Q0gYXot3RAQjGQAAAcRtuBuDYtUPjwAAAkKAECAwEBoAQAgnL4IEWB5LE/vWXLudaYwd8il06Rzrek5pd9TCOm8FDCRlEx0oZZ4VOvcucIihMYSiqChFZPUftTeQSXkXfpjbrGABEMSEkO5rKAASAA10gBZoEkggIfC1iCuX4nc2G4wq+hNHOlehBP1bZBAz4M8NEABUozOq2u80HZKRwE406KNp2oVnWAx2ObOHVjccHWn/NQ7msoAAYUWGAAAAOJgSOmBMWqHx4AAAAAKbKwkDE5MrK9MpB4T8ZFQBMtbAk=",
      "transaction_id": {
        "@type": "internal.transactionId",
        "lt": "1944556000003",
        "hash": "swpaG6pTBXwYI2024NAisIFp59Fw3k1DRQ5fa5SuKAE="
      },
      "fee": "33",
      "storage_fee": "33",
      "other_fee": "0",
      "in_msg": {
        "@type": "raw.message",
        "source": "EQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aJ9R",
        "destination": "EQAVKMzqtrvNB2SkcBONOijadqFZ1gMdjmzh1Y3HB1p_zai5",
        "value": "1000000000",
        "fwd_fee": "666672",
        "ihr_fee": "0",
        "created_lt": "1944556000002",
        "body_hash": "kBfGYBTkBaooeZ+NTVR0EiVGSybxQdb/ifXCRX5O7e0=",
        "msg_data": {
          "@type": "msg.dataText",
          "text": "U2VhIGJyZWV6ZSDwn4yK"
        },
        "message": "Sea breeze 🌊"
      },
      "out_msgs": []
    },
    {
      "@type": "raw.transaction",
      "utime": 1658126823,
      "data": "te6cckECBQEAASMAA7NxUozOq2u80HZKRwE406KNp2oVnWAx2ObOHVjccHWn/NAAABxG24G4OTlT0DAhE0aELXSEcncwE49P/9vECBbl31+UWLCvVJqgAAAa2t3liDYtUB5wAABBI2gBAgMBAaAEAIJyKqjqNU0guBAa3/ENp+bnQLlnXhkASZW2OWeFM5DakO/4IEWB5LE/vWXLudaYwd8il06Rzrek5pd9TCOm8FDCRgATDIJGyQ7msoABIADdSAFmgSSCAh8LWIK5fidzYbjCr6E0c6V6EE/VtkEDPgzw0QAFSjM6ra7zQdkpHATjToo2nahWdYDHY5s4dWNxwdaf81DuaygABhRYYAAAA4jbcDcExaoDzgAAAAApuDk0tzOQMze5Mrm6EHhPxllAGLZ+6g==",
      "transaction_id": {
        "@type": "internal.transactionId",
        "lt": "1943166000003",
        "hash": "hxIQqn7lYD/c/fNS7W/iVsg2kx0p/kNIGF6Ld0QEIxk="
      },
      "fee": "2331",
      "storage_fee": "2331",
      "other_fee": "0",
      "in_msg": {
        "@type": "raw.message",
        "source": "EQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aJ9R",
        "destination": "EQAVKMzqtrvNB2SkcBONOijadqFZ1gMdjmzh1Y3HB1p_zai5",
        "value": "1000000000",
        "fwd_fee": "666672",
        "ihr_fee": "0",
        "created_lt": "1943166000002",
        "body_hash": "7iirXn1RtliLnBUGC5umIQ6KTw1qmPk+wwJ5ibh9Pf0=",
        "msg_data": {
          "@type": "msg.dataText",
          "text": "U3ByaW5nIGZvcmVzdCDwn4yy"
        },
        "message": "Spring forest 🌲"
      },
      "out_msgs": []
    }
  ]
}
```

Мы получили последние две транзакции этого адреса. При добавлении к запросу `lt` и `hash`: мы снова получим две транзакции, однако вторая, станет следующей по счёту. То есть - мы получим вторую и третью транзакции этого адреса:

```json
{
  "ok": true,
  "result": [
    {
      "@type": "raw.transaction",
      "utime": 1658126823,
      "data": "te6cckECBQEAASMAA7NxUozOq2u80HZKRwE406KNp2oVnWAx2ObOHVjccHWn/NAAABxG24G4OTlT0DAhE0aELXSEcncwE49P/9vECBbl31+UWLCvVJqgAAAa2t3liDYtUB5wAABBI2gBAgMBAaAEAIJyKqjqNU0guBAa3/ENp+bnQLlnXhkASZW2OWeFM5DakO/4IEWB5LE/vWXLudaYwd8il06Rzrek5pd9TCOm8FDCRgATDIJGyQ7msoABIADdSAFmgSSCAh8LWIK5fidzYbjCr6E0c6V6EE/VtkEDPgzw0QAFSjM6ra7zQdkpHATjToo2nahWdYDHY5s4dWNxwdaf81DuaygABhRYYAAAA4jbcDcExaoDzgAAAAApuDk0tzOQMze5Mrm6EHhPxllAGLZ+6g==",
      "transaction_id": {
        "@type": "internal.transactionId",
        "lt": "1943166000003",
        "hash": "hxIQqn7lYD/c/fNS7W/iVsg2kx0p/kNIGF6Ld0QEIxk="
      },
      "fee": "2331",
      "storage_fee": "2331",
      "other_fee": "0",
      "in_msg": {
        "@type": "raw.message",
        "source": "EQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aJ9R",
        "destination": "EQAVKMzqtrvNB2SkcBONOijadqFZ1gMdjmzh1Y3HB1p_zai5",
        "value": "1000000000",
        "fwd_fee": "666672",
        "ihr_fee": "0",
        "created_lt": "1943166000002",
        "body_hash": "7iirXn1RtliLnBUGC5umIQ6KTw1qmPk+wwJ5ibh9Pf0=",
        "msg_data": {
          "@type": "msg.dataText",
          "text": "U3ByaW5nIGZvcmVzdCDwn4yy"
        },
        "message": "Spring forest 🌲"
      },
      "out_msgs": []
    },
    {
      "@type": "raw.transaction",
      "utime": 1657873517,
      "data": "te6cckECBQEAARUAA7FxUozOq2u80HZKRwE406KNp2oVnWAx2ObOHVjccHWn/NAAABra3eWINHKamCzNyhJYhx3LFjT1LoOSb8t8/BKZD64tdlEozSkwAAAa2sQlvDYtEkbQAAAgKAECAwEBoAQAgnIWNBaoz9t25kiF2dzOj2M7gKcODZM65K9V66Bee1OTpSqo6jVNILgQGt/xDafm50C5Z14ZAEmVtjlnhTOQ2pDvABEMQEkO5rKAASAAxUgBZoEkggIfC1iCuX4nc2G4wq+hNHOlehBP1bZBAz4M8NEABUozOq2u80HZKRwE406KNp2oVnWAx2ObOHVjccHWn/NQ7msoAAYUWGAAAANbW7yxBMWiSNoAAAAAKbKxt7cyQB5Hn/Q=",
      "transaction_id": {
        "@type": "internal.transactionId",
        "lt": "1845458000003",
        "hash": "k5U9AwIRNGhC10hHJ3MBOPT//bxAgW5d9flFiwr1Sao="
      },
      "fee": "1",
      "storage_fee": "1",
      "other_fee": "0",
      "in_msg": {
        "@type": "raw.message",
        "source": "EQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aJ9R",
        "destination": "EQAVKMzqtrvNB2SkcBONOijadqFZ1gMdjmzh1Y3HB1p_zai5",
        "value": "1000000000",
        "fwd_fee": "666672",
        "ihr_fee": "0",
        "created_lt": "1845458000002",
        "body_hash": "XpTXquHXP64qN6ihHe7Tokkpy88tiL+5DeqIrvrNCyo=",
        "msg_data": {
          "@type": "msg.dataText",
          "text": "U2Vjb25k"
        },
        "message": "Second"
      },
      "out_msgs": []
    }
  ]
}
```

Запрос будет выглядеть вот так - `https://testnet.toncenter.com/api/v2/getTransactions?address=EQAVKMzqtrvNB2SkcBONOijadqFZ1gMdjmzh1Y3HB1p_zai5&limit=2&lt=1943166000003&hash=hxIQqn7lYD%2Fc%2FfNS7W%2FiVsg2kx0p%2FkNIGF6Ld0QEIxk%3D&to_lt=0&archival=true` 

Так же нам пригодится метод `detectAddress`.

Не уверен насчёт основной сети, но в тестовой сети, адрес моего кошелька в tonkeeper такой:
`kQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aCTb`, а когда я смотрю транзакцию в эксплорере то вместо моего адреса там 
`EQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aJ9R`.
Данный метод возвращает нам “нужный” адрес:

```json
{
  "ok": true,
  "result": {
    "raw_form": "0:b3409241010f85ac415cbf13b9b0dc6157d09a39d2bd0827eadb20819f067868",
    "bounceable": {
      "b64": "EQCzQJJBAQ+FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aJ9R",
      "b64url": "EQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aJ9R"
    },
    "non_bounceable": {
      "b64": "UQCzQJJBAQ+FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aMKU",
      "b64url": "UQCzQJJBAQ-FrEFcvxO5sNxhV9CaOdK9CCfq2yCBnwZ4aMKU"
    },
    "given_type": "friendly_bounceable",
    "test_only": true
  }
}
```

Нам нужен `b64url`.

Также, этот метод помогает нам проверить правильность адреса присланного пользователем.

По большому счёту, это всё, что нам нужно.

### Запросы к API, и что с ними дальше делать

Вернёмся в IDE. откроем файл `api.py`.

```python
import requests
import json
# Импортируем наш модуль db, так как отсюда будет удобно добавлять
# транзакции в базу данных
import db

# Это начало наших запросов
MAINNET_API_BASE = "https://toncenter.com/api/v2/"
TESTNET_API_BASE = "https://testnet.toncenter.com/api/v2/"

# Узнаём в какой сети работаем
with open('config.json', 'r') as f:
    config_json = json.load(f)
    MAINNET_API_TOKEN = config_json['MAINNET_API_TOKEN']
    TESTNET_API_TOKEN = config_json['TESTNET_API_TOKEN']
    MAINNET_WALLET = config_json['MAINNET_WALLET']
    TESTNET_WALLET = config_json['TESTNET_WALLET']
    WORK_MODE = config_json['WORK_MODE']

if WORK_MODE == "mainnet":
    API_BASE = MAINNET_API_BASE
    API_TOKEN = MAINNET_API_TOKEN
    WALLET = MAINNET_WALLET
else:
    API_BASE = TESTNET_API_BASE
    API_TOKEN = TESTNET_API_TOKEN
    WALLET = TESTNET_WALLET
```

Наша первая функция для работы с запросом `detectAddress`:

```python
def detect_address(address):
    url = f"{API_BASE}detectAddress?address={address}&api_key={API_TOKEN}"
    r = requests.get(url)
    response = json.loads(r.text)
    try:
        return response['result']['bounceable']['b64url']
    except:
        return False
```

На входе у нас - предполагаемый адрес, а на выходе, либо “нужный” нам для дальнейшей работы “правильный” адрес, либо Ложь.

Вы можете заметить, что в конце запроса появился API ключ. Он нужен для снятия ограничения на количество запросов к API. Без него мы ограничены одним запросом в секунду.

Следующая функция для `getTransactions`:

```python
def get_address_transactions():
    url = f"{API_BASE}getTransactions?address={WALLET}&limit=30&archival=true&api_key={API_TOKEN}"
    r = requests.get(url)
    response = json.loads(r.text)
    return response['result']
```

Данная функция возвращает последние 30 транзакций для нашего `WALLET`.

Здесь можно заметить `archival=true`, он нужен для того, чтобы мы брали транзакции только с узла с полной историей блокчейна. 

На выходе получаем список транзакций - [{0},{1},{…},{29}]. Список словарей, короче говоря.

И, наконец, последняя функция:

```python
def find_transaction(user_wallet, value, comment):
		# Получаем последние 30 транзакций
    transactions = get_address_transactions()
    for transaction in transactions:
				# Выбираем входящее "сообщение" - транзакцию
        msg = transaction['in_msg']
        if msg['source'] == user_wallet and msg['value'] == value and msg['message'] == comment:
						# При полном совпадении всех данных, проверяем, что эту транзакцию
						# мы не верифицировали ранее
            t = db.check_transaction(msg['body_hash'])
            if t == False:
								# Если нет - записываем в таблицу к верифицированным
								# и возвращаем True
                db.add_v_transaction(
                    msg['source'], msg['body_hash'], msg['value'], msg['message'])
                print("find transaction")
                print(
                    f"transaction from: {msg['source']} \nValue: {msg['value']} \nComment: {msg['message']}")
                return True
						# Если данная транзакция уже верифицированна -
						# проверяем остальные, может найдём нужную
            else:
                pass
		# Если в последних 30 транзакциях нет нужной - возвращаем False
		# Здесь можно дополнить код, чтобы посмотреть следующие 29 транзакций
		# Однако в рамках Примера это будет лишним.
    return False
```

На входе “правильный” адрес кошелька, сумма и комментарий. На выходе Истина если найдена нужная входящая транзакция и Ложь если нет.
