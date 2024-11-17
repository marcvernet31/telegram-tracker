import os
from datetime import datetime
from dotenv import load_dotenv
from telethon import functions                   # type: ignore
from telethon.sync import TelegramClient, events # type: ignore

from config import conditions, TARGET_CHANNEL_ID, BOT_USER_ID, TEST_TARGET_CHANNEL_ID

load_dotenv()

TOPIC_TITLES = {}

client = TelegramClient(
    'anon', 
    os.environ.get("API_ID"), 
    os.environ.get("API_HASH")
)
client.start()

def write_message(url, chat_title, message, topic_title, sender_username):
    title = f"💸💸💸 [{chat_title}] [{topic_title}] 💸💸💸 \n" if topic_title else f"💸💸💸 [{chat_title}] [topic not found] 💸💸💸 \n"
    message = f"Message from: {sender_username}\nMessage: {message} \n"
    url_message = f"✅ {url} \n" if url else "❌ URL not found\n"
    return title + message + url_message

def build_topic_titles(client):
    global TOPIC_TITLES

    topics = client(
        functions.channels.GetForumTopicsRequest(
            channel=TARGET_CHANNEL_ID, 
            offset_date=datetime.now(), 
            offset_id=-1, 
            offset_topic=-1, 
            limit=50
        )
    )

    for topic in topics.topics: TOPIC_TITLES[topic.id] = topic.title


def get_topic_id(message):
    if message.reply_to and message.reply_to.reply_to_msg_id:
        return message.reply_to.reply_to_msg_id
    elif message.reply_to and message.reply_to.reply_to_top_id:
        return  message.reply_to.reply_to_top_id
    return None

async def get_topic_title(chat, message):
    topic_id = get_topic_id(message)
    topic_title = TOPIC_TITLES.get(topic_id, None)
    if topic_id is not None and topic_title is None:
        # message is a reply and topic_id is the id of the parent message
        parent_message = await client.get_messages(chat, ids=topic_id)
        topic_id = get_topic_id(parent_message)
        topic_title = TOPIC_TITLES.get(topic_id, None)
    return topic_id, topic_title

@client.on(events.NewMessage(chats=[TARGET_CHANNEL_ID, TEST_TARGET_CHANNEL_ID]))
async def track_messages(event):

    message_id = event.message.id
    chat = await event.get_chat()
    sender = await event.get_sender()

    topic_id, topic_title = await get_topic_title(chat, event.message)

    if(conditions(sender.username, event.text)):
        # https://t.me/c/2083186778/20/433995
        
        url = f"https://t.me/c/{TARGET_CHANNEL_ID}/{topic_id}/{message_id}" if topic_id is not None else ""

        message = write_message(url, chat.title, event.text, topic_title, sender.username or sender.first_name)

        forward_message = (f"Chat: [{chat.title}] (Chat ID: {chat.id})\n"
                        f"Sender: {sender.username or sender.first_name}\n"
                        f"Message: {event.text}\n")
        forward_message += f"topicId: {topic_id} | topicTitle: {topic_title}\n ({url})"

        print(message)
        print("--------------------------------")
        await client.send_message(BOT_USER_ID, message)


build_topic_titles(client)
client.run_until_disconnected()
