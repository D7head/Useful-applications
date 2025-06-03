import asyncio
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js
from pywebio.platform.tornado import start_server as start_http_server
chat_msgs = []
online_users = set()
MAX_MESSAGES_COUNT = 100
PORT = 8080
async def main():
    global chat_msgs
    put_markdown("## � Добро пожаловать в онлайн чат!")
    put_markdown("**Как подключиться:**\n"
                 "1. Для доступа из другой сети вам нужно:\n"
                 "   - Узнать ваш внешний IP (можно через сервисы типа 2ip.ru)\n"
                 "   - Открыть порт {} на роутере (если есть)\n"
                 "   - Дать друзьям адрес: http://[ваш_IP]:{}\n"
                 "2. Или использовать ngrok/tunnel для проброса порта".format(PORT, PORT))

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)
    nickname = await input("Войти в чат", required=True, placeholder="Ваше имя",
                           validate=lambda n: "Такой ник уже используется!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)
    system_msg = f'📢 `{nickname}` присоединился к чату!'
    chat_msgs.append(('📢', system_msg))
    msg_box.append(put_markdown(system_msg))

    refresh_task = run_async(refresh_msg(nickname, msg_box))
    def on_close():
        if nickname in online_users:
            online_users.remove(nickname)
            leave_msg = f'📢 Пользователь `{nickname}` покинул чат!'
            chat_msgs.append(('📢', leave_msg))
            if 'msg_box' in globals():
                msg_box.append(put_markdown(leave_msg))

    defer_call(on_close)
    while True:
        data = await input_group("💭 Новое сообщение", [
            input(placeholder="Текст сообщения ...", name="msg"),
            actions(name="cmd", buttons=[
                "Отправить",
                {'label': "Выйти из чата", 'type': 'cancel'},
                {'label': "Список онлайн", 'type': 'button', 'value': 'online'}
            ])
        ], validate=lambda m: ('msg', "Введите текст сообщения!") if m["cmd"] == "Отправить" and not m['msg'] else None)

        if data is None or data['cmd'] == 'cancel':
            break
        elif data['cmd'] == 'online':
            toast(f"Онлайн: {', '.join(online_users)}", duration=3)
            continue
        msg = data['msg']
        chat_msgs.append((nickname, msg))
        msg_box.append(put_markdown(f"`{nickname}`: {msg}"))
    refresh_task.close()
    toast("Вы вышли из чата!")
    put_buttons(['Перезайти'], onclick=lambda btn: run_js('window.location.reload()'))
async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(0.5)
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]
            last_idx = len(chat_msgs) // 2
        else:
            last_idx = len(chat_msgs)
if __name__ == "__main__":
    print(f"Сервер чата запущен. Для доступа:")
    print(f"- В локальной сети: http://localhost:{PORT}")
    print(f"- Из интернета: http://[ваш_внешний_IP]:{PORT} (если порт открыт)")
    start_http_server(main, port=PORT, host='0.0.0.0', debug=True, cdn=False)
