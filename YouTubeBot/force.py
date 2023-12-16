import pyrogram.errors
from  pyrogram.enums import ChatMemberStatus
async def check_channel_member(app, chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return True
        else:
            print(member.status)
            return False
    except pyrogram.errors.exceptions.bad_request_400.ChatAdminRequired:
        return True
    except Exception as e:
        return False
