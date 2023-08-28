from time import time
from typing import Union

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery

whitelist_chats_ids = [-1001215314525, -1001289123241, -1001680867541]  # ID чатов в белом списке

ops = [123456, 12453]  # ID админов, на замену проверкам


async def admins_filter(_, __, q: CallbackQuery | Message):
    if isinstance(q, CallbackQuery):
        return bool(q.from_user.id in ops and q.message.chat.id in whitelist_chats_ids)
    else:
        return bool(q.from_user.id in ops and q.chat.id in whitelist_chats_ids)

admins = filters.create(admins_filter)


async def timestamper(data: str, basic_time: int = None) -> Union[tuple[int, str, int], None]:
    """Переводит строки вида "yx" в кортеж, содержащие готовый timestamp для поиска по БД, и данные для генерации сообщения.
    y это любое положительное число больше 0, а x это одно из обозначений временного отрезка (секунда (s), минута (min), и т.д)"""
    data_len = len(data)

    try:
        if data[-3:] == 'mon':
            timetype = 'mon'
            multiplicator = int(data[:(data_len - 3)])
        else:
            timetype = data[-1]
            multiplicator = int(data[:(data_len - 1)])
    except ValueError:
        return

    match timetype:
        case 's':
            seconds = 1
            timetypes = ['секунд', 'секунда', 'секунды', 'секунды', 'секунды', 'секунд', 'секунд', 'секунд', 'секунд',
                         'секунд']

        case 'm':
            seconds = 60
            timetypes = ['минут', 'минута', 'минуты', 'минуты', 'минуты', 'минут', 'минут', 'минут', 'минут', 'минут']

        case 'h':
            seconds = 3600
            timetypes = ['часов', 'час', 'часа', 'часа', 'часа', 'часов', 'часов', 'часов', 'часов', 'часов']

        case 'd':
            seconds = 86400
            timetypes = ['дней', 'день', 'дня', 'дня', 'дня', 'дней', 'дней', 'дней', 'дней', 'дней']

        case 'mon':
            seconds = 2628003  # 2628002,88 не очень жрется, пусть и будет пару секунд поверх, но это не критично
            timetypes = ['месяцев', 'месяц', 'месяца', 'месяца', 'месяца', 'месяцев', 'месяцев', 'месяцев', 'месяцев',
                         'месяцев']

        case 'y':
            seconds = 31536000
            timetypes = ['лет', 'год', 'года', 'года', 'года', 'лет', 'лет', 'лет', 'лет', 'лет']

        case _:
            return

    if basic_time is None:
        return int(time() - (seconds * multiplicator)), timetypes[int(str(multiplicator)[-1])], multiplicator

    else:
        return int(basic_time - (seconds * multiplicator)), timetypes[int(str(multiplicator)[-1])], multiplicator
