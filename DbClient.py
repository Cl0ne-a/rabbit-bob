import pymongo

MONGODB_URI = "mongodb://localhost:27017"
client = pymongo.MongoClient(MONGODB_URI)

# creating collection
collection = client.get_database('chatters')


# get or create chat/channel from collection
def chat(chat_name):
    return collection.get_collection(chat_name)


# save onr message
def collect_message(some_chat, some_post):
    chat(some_chat).insert_one(some_post)


# save list of messages
def save_history(some_chat, messages_history):
    chat(some_chat + '_history').insert_many(messages_history)


# date format example 13-04-2022
def read_chat_history(some_chat, from_date):
    date_greater_then = {
        'date': {
            '$gte': from_date + ' 00:00'
        }
    }
    return chat(some_chat).find(filter=date_greater_then)
