from telethon.utils import pack_bot_file_id
from userbot.modules.sql_helper.welcome_sql import get_current_welcome_settings, add_welcome_setting, rm_welcome_setting
from userbot.events import register
from userbot import CMD_HELP, bot, LOGS
from telethon.events import ChatAction


@bot.on(ChatAction)
async def _(event):
    cws = get_current_welcome_settings(event.chat_id)
    if cws:
        """user_added=False,
        user_joined=True,
        user_left=False,
        user_kicked=False,"""
        if event.user_joined:
            if cws.should_clean_welcome:
                try:
                    await event.client.delete_messages(
                        event.chat_id,
                        cws.previous_welcome
                    )
                except Exception as e:
                    LOGS.warn(str(e))
            a_user = await event.get_user()
            chat = await event.get_chat()

            title = chat.title if chat.title else "this chat"
            participants = await event.client.get_participants(chat)
            count = len(participants)
            current_saved_welcome_message = cws.custom_welcome_message
            mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
            first = a_user.first_name
            last = a_user.last_name
            if last:
                fullname = f"{first} {last}"
            else:
                fullname = first
            username = f"@{a_user.username}" if a_user.username else mention
            userid = a_user.id

            current_message = await event.reply(
                current_saved_welcome_message.format(mention=mention, title=title, count=count, first=first, last=last, fullname=fullname, username=username, userid=userid),
                file=cws.media_file_id
            )


@register(outgoing=True, pattern=r"^.welcome (.*)")
async def _(event):
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        if event.fwd_from:
            return
        msg = await event.get_reply_message()
        if msg and msg.media:
            bot_api_file_id = pack_bot_file_id(msg.media)
            if add_welcome_setting(event.chat_id, msg.message, True, 0, bot_api_file_id) is True:
                await event.edit("Welcome message saved.")
            else:
                await event.edit("I can save only one welcome note !!")
        elif msg and not msg.media:
            if add_welcome_setting(event.chat_id, msg.message, True, 0) is True:
                await event.edit("Welcome message saved.")
            else:
                await event.edit("I can save only one welcome note !!")
        else:
            input_str = event.pattern_match.group(1)
            if add_welcome_setting(event.chat_id, input_str, True, 0) is True:
                await event.edit("Welcome message saved.")
            else:
                await event.edit("I can save only one welcome note !!")


@register(outgoing=True, pattern="^.showwelcome$")
async def _(event):
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        if event.fwd_from:
            return
        cws = get_current_welcome_settings(event.chat_id)
        await event.edit(f"The current welcome message is:\n{cws.custom_welcome_message}")


@register(outgoing=True, pattern="^.clearwelcome")
async def _(event):
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        if event.fwd_from:
            return
        rm_welcome_setting(event.chat_id)
        await event.edit("Welcome note cleared for this chat.")


CMD_HELP.update({
    "welcome": "\
.welcome <notedata/reply>\
\nUsage: Saves (or updates) notedata / replied message as a welcome note in the chat.\
\nAvailable variables for formatting welcome messages : {mention}, {title}, {count}, {first}, {last}, {fullname}, {userid}, {username}\
\n\n.showwelcome\
\nUsage: Gets your current welcome message in the chat.\
\n\n.clearwelcome\
\nUsage: Deletes the welcome note for the current chat.\
"})
