from telebot.types import Message
from .admin import is_user_admin, is_bot_admin

def set_welcome(bot, db):
    @bot.message_handler(commands=['welcome'])
    def set_welcome_message(message: Message):
        if message.chat.type == 'private':
            bot.reply_to(message, "This command can only be used in groups.")
            return
        
        try:
            if not is_user_admin(bot, message.chat, message.from_user.id):
                bot.reply_to(message, "You are not an admin in this group.")
                return

            if not is_bot_admin(bot, message.chat.id):
                bot.reply_to(message, "I am not an admin in this group.")
                return

            group_id = message.chat.id
            command_parts = message.text.split(' ', 1)
            
            if len(command_parts) == 1:
                bot.reply_to(message, "Usage: /welcome [on/off] [message]\nExample: /welcome on {name} Welcome to {group}!")
                return

            action = command_parts[1].split(' ')[0].lower()

            if action == 'on':
                welcome_message = ' '.join(command_parts[1].split(' ')[1:])
                if not welcome_message:
                    bot.reply_to(message, f"Usage: /welcome on {{name}} Welcome to {message.chat.title}!")
                    return
                db.messages.update_one({"_id": group_id}, {"$set": {"welcome_message": welcome_message, "welcome_enabled": True}}, upsert=True)
                bot.reply_to(message, "Welcome message enabled and set successfully!")
            elif action == 'off':
                db.messages.update_one({"_id": group_id}, {"$set": {"welcome_enabled": False}}, upsert=True)
                bot.reply_to(message, "Welcome message disabled successfully!")
            else:
                bot.reply_to(message, "Invalid action. Use 'on' to enable and 'off' to disable.")
        except Exception as e:
            bot.reply_to(message, f"An error occurred: {e}")

def set_goodbye(bot, db):
    @bot.message_handler(commands=['goodbye'])
    def set_goodbye_message(message: Message):
        if message.chat.type == 'private':
            bot.reply_to(message, "This command can only be used in groups.")
            return
        
        try:
            if not is_user_admin(bot, message.chat, message.from_user.id):
                bot.reply_to(message, "You are not an admin in this group.")
                return

            if not is_bot_admin(bot, message.chat.id):
                bot.reply_to(message, "I am not an admin in this group.")
                return

            group_id = message.chat.id
            command_parts = message.text.split(' ', 1)
            
            if len(command_parts) == 1:
                bot.reply_to(message, "Usage: /goodbye [on/off] [message]\nExample: /goodbye on Goodbye {name}. Hope to see you again in {group}!")
                return

            action = command_parts[1].split(' ')[0].lower()

            if action == 'on':
                goodbye_message = ' '.join(command_parts[1].split(' ')[1:])
                if not goodbye_message:
                    bot.reply_to(message, f"Usage: /goodbye on Goodbye {{name}}. Hope to see you again in {message.chat.title}!")
                    return
                db.messages.update_one({"_id": group_id}, {"$set": {"goodbye_message": goodbye_message, "goodbye_enabled": True}}, upsert=True)
                bot.reply_to(message, "Goodbye message enabled and set successfully!")
            elif action == 'off':
                db.messages.update_one({"_id": group_id}, {"$set": {"goodbye_enabled": False}}, upsert=True)
                bot.reply_to(message, "Goodbye message disabled successfully!")
            else:
                bot.reply_to(message, "Invalid action. Use 'on' to enable and 'off' to disable.")
        except Exception as e:
            bot.reply_to(message, f"An error occurred: {e}")

def welcome_goodbye_handler(bot, db):
    @bot.message_handler(content_types=['new_chat_members'])
    def welcome_new_members(message: Message):
        if message.chat.type == 'private':
            return
        
        try:
            group_id = message.chat.id
            group_data = db.messages.find_one({"_id": group_id})
            if group_data and group_data.get("welcome_enabled", False) and "welcome_message" in group_data:
                for new_member in message.new_chat_members:
                    welcome_text = group_data["welcome_message"].replace('{name}', f"[{new_member.first_name}](tg://user?id={new_member.id})").replace('{group}', message.chat.title)
                    bot.send_message(
                        message.chat.id, 
                        welcome_text,
                        parse_mode='Markdown'
                    )
        except Exception as e:
            print(f"An error occurred: {e}")

    @bot.message_handler(content_types=['left_chat_member'])
    def goodbye_left_member(message: Message):
        if message.chat.type == 'private':
            return
        try:
            group_id = message.chat.id
            group_data = db.messages.find_one({"_id": group_id})
            if group_data and group_data.get("goodbye_enabled", False) and "goodbye_message" in group_data:
                goodbye_text = group_data["goodbye_message"].replace('{name}', f"[{message.left_chat_member.first_name}](tg://user?id={message.left_chat_member.id})").replace('{group}', message.chat.title)
                bot.send_message(
                    message.chat.id, 
                    goodbye_text,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"An error occurred: {e}")
