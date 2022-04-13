from telethon import TelegramClient, events
import DbClient as db

# change to your own  api_id and api_hash from https://telegram.org/
api_id = 14434841
api_hash = '0acd5bb421d68b4a006454465de4fa78'

telegram_client = TelegramClient('HannaShchur', api_id, api_hash)

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
    db.collect_message(chat_name, message)


telegram_client.start()

# get all the history in the channel:

messages_history = telegram_client.iter_messages(chat_name)

# with TelegramClient('HannaShchur', api_id, api_hash) as client:
history = []


if chat_name[0].__eq__('@'):
    for message in messages_history:
        if len(history) < 5:
            date = message.date
            user_id = message.peer_id.user_id
            message_text = message.message
            element = {'date': date, 'user_id': user_id, 'message': message_text}
            history.append(element)
        else:
            break
else:
    for message in messages_history:
        if len(history) < 25:
            date = message.date
            message_text = message.message
            element = {'date': date, 'message': message_text}
            history.append(element)
        else:
            break


# for message in list(db.read_chat_history(chat_name, '01-04-2022')):
#     if len(history) < 100:
#         message_date = message.get('date')
#         message_sender_id = message.get('user_id')
#         message_text = message.get('message')
#         element = {'date': message_date, 'user_id': message_sender_id, 'message': message_text}
#         history.append(element)


db.save_history(chat_name, history)

telegram_client.run_until_disconnected()
