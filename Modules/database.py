import Modules.misc as misc

from sqlite3 import Connection


async def get_users(chat_id: int, conn: Connection, target_time: int | str) -> list[(int,)]:
    if isinstance(target_time, int):
        return conn.execute('SELECT user_id FROM users WHERE chat_id = %s AND time >= %s;', (chat_id, target_time)).fetchall()
    else:
        return conn.execute('SELECT user_id FROM users WHERE chat_id = %s AND date_registered >= %s::DATE;',
                            (chat_id, target_time)).fetchall()


async def clear(conn: Connection):
    conn.execute('DELETE FROM users WHERE time < %s;', ((await misc.timestamper('4d'))[0],))
