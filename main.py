import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired
from pyrogram.types import Message
import time
import os

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
ss = os.environ.get("STRING", "")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    await m.reply_text("**I am a bot. Send an invitation link to clone messages automatically from a public channel.**")

@bot.on_message(filters.text)
async def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    # Joining public channels
    if "https://t.me/" in message.text:
        chat_username = message.text.split('/')[-1]  # Extract the channel username from the link

        try:
            async with acc:
                await acc.join_chat(chat_username)  # Join the channel
            await bot.send_message(message.chat.id, "**Successfully joined the channel. Now cloning messages...**", reply_to_message_id=message.id)

            # Clone all messages from the public channel
            await clone_all_messages(chat_username, message.chat.id)
        except UserAlreadyParticipant:
            await bot.send_message(message.chat.id, "**Already a participant in the channel.**", reply_to_message_id=message.id)
        except Exception as e:
            await bot.send_message(message.chat.id, f"**Error: {str(e)}**", reply_to_message_id=message.id)

async def clone_all_messages(chat_username, destination_chat_id):
    async with acc:
        async for msg in acc.get_chat_history(chat_username):
            # Check if the message contains text or other media types
            if msg.text:
                await bot.send_message(destination_chat_id, msg.text, entities=msg.entities)
            elif msg.document:
                await bot.send_document(destination_chat_id, msg.document.file_id, caption=msg.caption)
            elif msg.video:
                await bot.send_video(destination_chat_id, msg.video.file_id, caption=msg.caption)
            elif msg.photo:
                await bot.send_photo(destination_chat_id, msg.photo.file_id, caption=msg.caption)
            elif msg.audio:
                await bot.send_audio(destination_chat_id, msg.audio.file_id, caption=msg.caption)
            elif msg.animation:
                await bot.send_animation(destination_chat_id, msg.animation.file_id)
            elif msg.voice:
                await bot.send_voice(destination_chat_id, msg.voice.file_id, caption=msg.caption)
            elif msg.sticker:
                await bot.send_sticker(destination_chat_id, msg.sticker.file_id)
            time.sleep(1)  # Optional delay to avoid hitting API limits

# Start the bot
bot.run()
