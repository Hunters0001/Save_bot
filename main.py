import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired
from pyrogram.types import Message
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_token = os.environ.get("TOKEN", "") 
api_hash = os.environ.get("HASH", "") 
api_id = os.environ.get("ID", "")
ss = os.environ.get("STRING", "")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)

@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, message: Message):
    await message.reply_text("**I am a clone bot. Send an invitation link to clone all messages from the chat.**")

@bot.on_message(filters.text)
async def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:
        try:
            chat_link = message.text.strip()
            async with acc:
                await acc.join_chat(chat_link)  # Join the chat using the invitation link
                await message.reply_text("**Successfully joined the chat! Now cloning messages...**")
                
                # Get chat ID from the link
                chat_id = chat_link.split('/')[-1]
                await clone_all_messages(chat_id, message.chat.id)  # Clone messages to the target chat
                
        except UserAlreadyParticipant:
            await message.reply_text("**Already a participant in the chat.**")
        except InviteHashExpired:
            await message.reply_text("**The invitation link has expired.**")
        except Exception as e:
            logger.error(f"Error joining chat: {e}")
            await message.reply_text("**An error occurred while trying to join the chat.**")

async def clone_all_messages(chat_id, target_chat_id):
    async with acc:
        try:
            messages = await acc.get_chat_history(chat_id)  # Get all messages from the chat
            async for msg in messages:
                if msg.text:
                    await bot.send_message(target_chat_id, msg.text)
                elif msg.document:
                    await bot.send_document(target_chat_id, msg.document.file_id, caption=msg.caption)
                elif msg.video:
                    await bot.send_video(target_chat_id, msg.video.file_id, caption=msg.caption)
                elif msg.photo:
                    await bot.send_photo(target_chat_id, msg.photo.file_id, caption=msg.caption)
                time.sleep(1)  # Optional delay to avoid hitting rate limits
            logger.info(f"Cloned messages from chat ID {chat_id} to target chat ID {target_chat_id}")
        except Exception as e:
            logger.error(f"Error cloning messages: {e}")

# Run the bot
if __name__ == "__main__":
    bot.run()
