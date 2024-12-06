import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired
from pyrogram.types import Message

import time
import os
import threading

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
ss = os.environ.get("STRING", "")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    await m.reply_text("**I am a simple save restricted bot**.\n\nSend message link or channel invite link to clone/download here\n Must join:- @Bypass_restricted")

@bot.on_message(filters.command(["bulk"]))
async def account_login(bot: Client, m: Message):
    await m.reply_text("**I am not an advanced bot**")

# Clone all messages from the joined chat
def clone_all_messages(chat_id, target_chat_id):
    with acc:
        messages = acc.get_chat_history(chat_id)  # Get all messages from the chat
        for msg in messages:
            if msg.text:  # If the message is a text message
                bot.send_message(target_chat_id, msg.text)
            elif msg.document:  # If the message is a document
                bot.send_document(target_chat_id, msg.document.file_id, caption=msg.caption)
            elif msg.video:  # If the message is a video
                bot.send_video(target_chat_id, msg.video.file_id, caption=msg.caption)
            elif msg.photo:  # If the message is a photo
                bot.send_photo(target_chat_id, msg.photo.file_id, caption=msg.caption)
            # Add more conditions for other media types as needed
            time.sleep(1)  # Optional: Delay to avoid hitting rate limits

@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    # Joining chats
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        try:
            with acc:
                acc.join_chat(message.text)
            bot.send_message(message.chat.id, "**Successfully joined the chat**", reply_to_message_id=message.id)
            chat_id = message.text.split('/')[-1]  # Extract the chat ID from the link
            clone_all_messages(chat_id, message.chat.id)
        except UserAlreadyParticipant:
            bot.send_message(message.chat.id, "**Already a participant in the chat**", reply_to_message_id=message.id)
        except InviteHashExpired:
            bot.send_message(message.chat.id, "**Link has expired.**", reply_to_message_id=message.id)

# Infinity polling
bot.run()
