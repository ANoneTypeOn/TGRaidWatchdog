from psycopg_pool import ConnectionPool
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import datetime

success = 'Пользователь с id {user_id} был успешно забанен\n'
failure = 'Пользователь с id {user_id} не был забанен\n'

no_data = 'За этот период записей нет'

help_t = """Бот представляет из себя простой функционал по очистке чата от ботов по временным отрезкам. Активируется \
очистка через команду `/clear` по следующим сценариям:

1) `/clear` (аргумент, предоставляющий временной отрезок в формате ddtt (где dd-это число, а tt это буквенное условное \
обозначение временного отрезка. Доступны: s(секунда), m(минута), h(час), d(день), mon(месяц), и y(год). \
При правильно введенном аргументе бот возьмет все записи, начиная с соответствующей даты, и кикнет всех зашедших в то \
время из чата

Спешу заметить, что бот хранит пользователей в базе данных, которая хранит записи за четыре последних дня, так что все \
промежутки больше четырех дней не имеют смысла, и будут всего-навсего выбирать все доступные записи

2) `/clear`. Отправит ответ на сообщение клавиатурой всех доступных дат. При нажатии на соответствующую кнопку бот \
начнет процедуру очистки, полагаясь на нее как на отправную точку для зачистки

После окончания процесса в чат будет скинут файл с итогами"""


async def generate_actions(pool: ConnectionPool) -> (str, InlineKeyboardMarkup):
    text = """Выберите вариант зачистки по датам из ниже предложенных, или введите команду повторно с аргументом в \
виде, который указан в документации"""

    with pool.connection() as conn:
        data = conn.execute('SELECT DISTINCT date_registered FROM users;').fetchall()

    buttons = []

    for date, in data:
        sdate = date.isoformat()

        buttons.append([InlineKeyboardButton(datetime.date.fromisoformat(sdate).strftime('%d.%m.%Y'), sdate)])

    return text, InlineKeyboardMarkup(buttons)
