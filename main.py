import time
import aiohttp
import os

from pyrogram import Client, filters, errors
from pyrogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import date
from configparser import ConfigParser

from Modules import database, templates, misc


config = ConfigParser()
config.read('config.ini')

bot_token = config.get('pyrogram', 'bot_token')

client = Client('bot', config_file='config.ini')

conn = client.storage.conn


@client.on_callback_query(misc.admins)
async def queries(_, query: CallbackQuery):
    if query.data is not None:
        timediff = date.today() - date.fromisoformat(query.data)
        tstamp = await misc.timestamper(f'{timediff.days}d')
        if tstamp is None:
            return

        _, word, mcounter = tstamp

        users = await database.get_users(query.message.chat.id, conn, query.data)
        if not users:
            await query.message.reply_to_message.reply(templates.no_data)
            return

        else:
            await query.message.reply_to_message.reply(f'Зачистка за {mcounter} {word} была инициализирована')

            async with aiohttp.ClientSession() as session:
                reports = [None]
                cleared = 0
                not_cleared = 0

                for user_id, in users:
                    request_args = {
                        'chat_id': query.message.chat.id,
                        'user_id': user_id,
                        'until_date': int(time.time() + 60)
                    }

                    # Чтобы не тянуть целую либу ради одного метода был использован POST запрос
                    async with session.post(f'https://api.telegram.org/bot{bot_token}/banChatMember',
                                            json=request_args) as response:
                        if response.ok:
                            reports.append(str(templates.failure).format(user_id=user_id))
                            not_cleared += 1
                        else:
                            reports.append(str(templates.success).format(user_id=user_id))
                            cleared += 1

                reports[0] = f'В общем зачищено {cleared}, не зачищено {not_cleared}\n'

                open('report.txt', 'w+').writelines(reports)
                await query.message.reply_to_message.reply_document('report.txt')
                os.remove('report.txt')


@client.on_message(filters.new_chat_members)
async def main(_, msg: Message):
    conn.execute('INSERT INTO users VALUES (%s, %s, %s, %s);', (msg.chat.id, msg.from_user.id, time.time(),
                                                                date.today()))


@client.on_message(filters.command('clear') & misc.admins)
async def clear(_, msg: Message):
    msg_split = msg.text.split()

    if len(msg_split) > 1:
        tstamp = await misc.timestamper(msg_split[1])
        if tstamp is None:
            return

        border, word, mcounter = tstamp
    else:
        text, reply_markup, = await templates.generate_actions(conn)

        try:
            await msg.reply(text, reply_markup=reply_markup)
        except errors.ReplyMarkupInvalid:
            await msg.reply('Данных нет. Вообще')

        return

    users = await database.get_users(msg.chat.id, conn, border)

    if not users:
        await msg.reply(templates.no_data)
        return

    else:
        await msg.reply(f'Зачистка за {mcounter} {word} была инициализирована')

        async with aiohttp.ClientSession() as session:
            reports = [None]
            cleared = 0
            not_cleared = 0

            for user_id, in users:
                request_args = {
                    'chat_id': msg.chat.id,
                    'user_id': user_id,
                    'until_date': int(time.time() + 60)
                }
    
                async with session.post(f'https://api.telegram.org/bot{bot_token}/banChatMember', json=request_args) as response:
                    if response.ok:
                        reports.append(str(templates.failure).format(user_id=user_id))
                    else:
                        reports.append(str(templates.success).format(user_id=user_id))

            reports[0] = f'В общем зачищено {cleared}, не зачищено {not_cleared}\n'

            open('report.txt', 'w+').writelines(reports)
            await msg.reply_document('report.txt')
            os.remove('report.txt')


@client.on_message(filters.command('help') & misc.admins)
async def b_help(_, msg: Message):
    await msg.reply(templates.help_t)


@client.on_message(filters.command('gban') & misc.admins)
async def gban(_, msg: Message):
    await msg.delete()

    if msg.reply_to_message is not None:
        target_id = msg.reply_to_message.from_user.id
    elif len(msg.text.split()) > 1:
        try:
            target = await client.get_chat_member(msg.chat.id, msg.text.split()[1])
        except:
            return

        target_id = target.user.id
    else:
        return

    for chat in misc.whitelist_chats_ids:
        try:
            await client.ban_chat_member(chat, target_id)
        except:
            continue


@client.on_message(filters.command('ungban') & misc.admins)
async def gunban(_, msg: Message):
    await msg.delete()

    if msg.reply_to_message is not None:
        target_id = msg.reply_to_message.from_user.id
    elif len(msg.text.split()) > 1:
        try:
            target = await client.get_chat_member(msg.chat.id, msg.text.split()[1])
        except:
            return

        target_id = target.user.id
    else:
        return

    for chat in misc.whitelist_chats_ids:
        try:
            await client.unban_chat_member(chat, target_id)
        except:
            continue


@client.on_chat_member_updated()
async def leave(_, msg):
    if msg.chat.id not in misc.whitelist_chats_ids:
        await client.leave_chat(msg.chat.id)


scheduler = AsyncIOScheduler()
scheduler.add_job(database.clear, args=(conn,))
scheduler.start()

client.run()
scheduler.shutdown()
