from telethon import TelegramClient, events
import DbClient as db
import argparse


# change to your own  api_id and api_hash from https://telegram.org/
api_id = 14434841
api_hash = '0acd5bb421d68b4a006454465de4fa78'
parser = argparse.ArgumentParser('set_history_length')
telegram_client = TelegramClient('Rabbit Bob', api_id, api_hash)

parser.add_argument("-id", help="set client api_id", type=int)
parser.add_argument("-hash", help="set client api_hash", type=str)
parser.add_argument("--limit", "-L", help="limits the history length to certain length", type=int, default=10)

args = parser.parse_args()

print('Input chat to read: \n')
chat_name = input()


@telegram_client.on(events.NewMessage(chats=chat_name))
async def normal_handler(event):
    user_mess = event.message.to_dict()['message']

    s_user_id = event.message.to_dict()['from_id']

    mess_date = event.message.to_dict()['date'].strftime("%d-%m-%Y %H:%M")

    message = {'date': mess_date,
               'user_id': s_user_id,
               'message': user_mess}
    db.save_message(chat_name, message)


telegram_client.start()

# get all the history in the channel:
messages_history = telegram_client.iter_messages(chat_name, args.limit)

# with TelegramClient('HannaShchur', api_id, api_hash) as client:
history = []

if chat_name[0].__eq__('@'):
    for message in messages_history:
        date = message.date
        user_id = message.peer_id.user_id
        message_text = message.message
        element = {'date': date, 'user_id': user_id, 'message': message_text}
        history.append(element)

else:
    for message in messages_history:
        date = message.date
        message_text = message.message
        element = {'date': date, 'message': message_text}
        history.append(element)

db.save_history(chat_name, reversed(history))

telegram_client.run_until_disconnected()
