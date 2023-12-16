from config import Config
import json
import youtube_search
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.types import (
    ForceReply, InlineKeyboardMarkup as Markup , InlineKeyboardButton as Button,
    InputMediaVideo, InputMediaAudio, InputMediaPhoto
)
from pyrogram import emoji
from pyrolistener import Listener
from pyrolistener.exceptions import TimeOut
from pySmartDL import SmartDL
from requests import Session
from datetime import datetime
from asyncio import sleep, create_task
from threading import Thread
import os

app = Client(
    "YouTubeSearch",
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.TG_BOT_TOKEN,
)
listener = Listener(client = app)
session = Session()
url_prefix = 'https://www.youtube.com'

def FetchLink(link, format = 'video'):
    return yt_dlp.YoutubeDL(
        {"format": "bestaudio[ext=m4a]" if format == "audio" else "best"}).extract_info(
            url=link,
            download=False
        )["url"]


def Fetch(link):
    return json.dumps(
        yt_dlp.YoutubeDL().extract_info(
            url=link,
            download=False
        ),
        ensure_ascii=False,
        indent=4
    )

def Search(query):
    return json.dumps(
        youtube_search.YoutubeSearch(query, max_results=5).to_dict(),
        ensure_ascii=False,
        indent=4
    )


@app.on_message(filters.command('start'))
async def start(_: Client , message: Message):
    await message.reply(
        '- I\'m a YouTube Searcher Bot.\n\n- Use /help to Get Help',
        reply_to_message_id = message.id
    )
    
@app.on_message(filters.command('help'))
async def _help(_: Client , message: Message):
    await message.reply(
        '1. /search Command Is To Search About a Word in YouTube.\n\n2. /get Command Is To Get a Video URL Info.\n\n3. /download Command Is To Download a Video and Upload it To Telegram.',
    )
    
@app.on_message(filters.command('search'))
async def search(_: Client , message: Message):
    user_id = message.from_user.id
    try: ask = await listener.listen(
             from_id = user_id,
             chat_id = message.chat.id,
             text = '- Well, Send Me a Word to Start Searching!\n\n- Use /cancel to Cancel the Process.',
             reply_markup = ForceReply(selective = True, placeholder = 'Entre Your Word: '),
             reply_to_message_id = message.id,
             timeout = 30
         )
    except TimeOut: return await message.reply('- time to recieve a search word ran out.'.title(), reply_to_message_id = message.id)
    if ask.text == '/cancel': return await ask.reply('- the process was canceled'.title(), reply_to_message_id = ask.id)
    wait_msg = await ask.reply(emoji.MAGNIFYING_GLASS_TILTED_RIGHT)
    results = json.loads(Search(ask.text))
    if len(results) == 0: return await wait_msg.edit_text('- no results was found'.title(), reply_to_message_id = ask.id)
    ids = ' '.join([result['id'] for result in results])
    callback_data = f'next 0 {ask.text}'
    firstone = results[0]
    yturl = url_prefix + firstone['url_suffix']
    title = firstone['title']
    duration = firstone['duration']
    views = firstone['views']
    publish_time = firstone['publish_time']
    thumbnail = Thumbnail(firstone['thumbnails'][-1], firstone['id'])
    author = firstone['channel']
    markup = Markup([
        [
            Button('- Upload To Telegram -', callback_data = f'download {firstone["id"]} {ask.id}'),
        ],
        [
            Button('- First Result -', callback_data = 'nothing'),
            Button('- Next -', callback_data = callback_data)
        ],
        [
            Button('- YouTube -', url = yturl)
        ]
    ])
    caption = f'- Title : {title}\n\n- Duration : {duration}\n\n- Views : {views.replace("مشاهدة", "view")}\n\n- Publish Since: {publish_time}\n\n- channel : {author}'
    await ask.reply_photo( 
        photo = thumbnail, 
        caption = caption, 
        reply_markup = markup, 
        reply_to_message_id = ask.id
    )
    await wait_msg.delete()


@app.on_message(filters.command('get'))
async def get(_: Client , message: Message):
    user_id = message.from_user.id
    try: ask = await listener.listen(
             from_id = user_id,
             chat_id = message.chat.id,
             text = '- Well, Send Me a YouTube Video URL to Get Info About It!\n\n- Use /cancel to Cancel the Process.',
             reply_markup = ForceReply(selective = True, placeholder = 'A Video URL: '),
             reply_to_message_id = message.id,
             timeout = 30
         )
    except TimeOut: return await message.reply('- time to recieve a youtube video url ran out.'.title(), reply_to_message_id = message.id)
    if ask.text == '/cancel': return await ask.reply('- the process was canceled'.title(), reply_to_message_id = ask.id)
    elif ask.text in ['http://www.youtube.com', 'www.youtube.com', 'youtube.com']: return await ask.reply('- Invalid URL!', reply_to_message_id = ask.id)
    wait_msg = await ask.reply(emoji.MAGNIFYING_GLASS_TILTED_RIGHT)
    try:result = json.loads(Fetch(ask.text))
    except yt_dlp.utils.DownloadError:
        await wait_msg.delete()
        return await ask.reply('- Invalid URL!', reply_to_message_id = ask.id)
    _id = result['id']
    title = result['title']
    try:thumbnail = Thumbnail(result['thumbnail'], _id)
    except:thumbnail = 'default.png'
    views = '{:,}'.format(result['view_count'])
    duration = result['duration_string']
    channel = result['channel']
    followers = '{:,}'.format(result['channel_follower_count'])
    publish_date = str(datetime.strptime(result['upload_date'], '%Y%m%d')).split()[0]
    markup = Markup([
        [Button('- Upload To Telegram - ', callback_data = f'download {_id} {ask.id}')]
    ])
    caption = f'- Title : {title}\n\n- Duration : {duration}\n\n- Views : {views} view\n\n- Published At : {publish_date}\n\n'
    caption += f'- Channel : {channel}\n\n- Subscribers : {followers}'
    await ask.reply_photo(
        photo = thumbnail,
        caption = caption,
        reply_markup = markup,
        reply_to_message_id = ask.id
    )
    await wait_msg.delete()


@app.on_message(filters.command('download'))
async def download(_: Client , message: Message):
    user_id = message.from_user.id
    try: ask = await listener.listen(
             from_id = user_id,
             chat_id = message.chat.id,
             text = '- Well, Send Me a YouTube Video URL To Download it!\n\n- Use /cancel to Cancel the Process.',
             reply_markup = ForceReply(selective = True, placeholder = 'A Video URL: '),
             reply_to_message_id = message.id,
             timeout = 30
         )
    except TimeOut: return await message.reply('- time to recieve a youtube video url ran out.'.title(), reply_to_message_id = message.id)
    if ask.text == '/cancel': return await ask.reply('- the process was canceled'.title(), reply_to_message_id = ask.id)
    elif ask.text in ['http://www.youtube.com', 'www.youtube.com', 'youtube.com']: return await ask.reply('- Invalid URL!', reply_to_message_id = ask.id)
    try: type = await listener.listen(
             from_id = user_id,
             chat_id = message.chat.id,
             text = '- Choose a Format:\n- v For Video.\n- a For Audio.\n\n- Use /cancel to Cancel the Process.',
             reply_markup = ForceReply(selective = True, placeholder = 'Format: '),
             reply_to_message_id = message.id,
             timeout = 30
         )
    except TimeOut: return await message.reply('- time to recieve the format ran out.'.title(), reply_to_message_id = message.id)
    if type.text == '/cancel': return await type.reply('- the process was canceled'.title(), reply_to_message_id = type.id)
    elif type.text.lower() not in ['v', 'a']: return await type.reply('Invalid Format!', reply_to_message_id = type.id)
    create_task(downloadURL(ask ,ask.text, type.text.lower()))
    

@app.on_callback_query(filters.regex(r'^(download)'))
async def upload_to_telegram(_: Client , callback: CallbackQuery):
    data = callback.data.split()
    yturl = f'https://www.youtube.com/watch?v={data[1]}'
    await callback.message.edit_text('- Choose a Format:\n- v For Video.\n- a For Audio.\n\n- Use /cancel to Cancel the Process.')
    try: type = await listener.listen(
        chat_id = callback.message.chat.id,
        from_id = callback.from_user.id,
        reply_markup = ForceReply(selective = True, placeholder = 'Format: '),
        reply_to_message_id = callback.message.id,
        timeout = 30
        )
    except TimeOut: return await message.reply('- time to recieve the format ran out.'.title(), reply_to_message_id = message.id)
    if type.text == '/cancel': return await type.reply('- the process was canceled'.title(), reply_to_message_id = type.id)
    elif type.text.lower() not in ['v', 'a']: return await type.reply('Invalid Format!', reply_to_message_id = type.id)
    create_task(downloadURL(type , yturl, type.text.lower()))

@app.on_callback_query(filters.regex(r'^(next)'))
async def _next(_: Client , callback: CallbackQuery):
    data = callback.data.split(maxsplit=2)[1:]
    index = data[0]
    keyword = data[1]
    await callback.answer('- Please, Wait a Moment..!', cache_time = 5)
    results = json.loads(Search(keyword))
    callback_data = f'next {int(index) + 1} {keyword}' if int(index) + 1 != 4 else 'nothing'
    choosed = results[int(index) + 1]
    yturl = url_prefix + choosed['url_suffix']
    title = choosed['title']
    duration = choosed['duration']
    views = choosed['views']
    publish_time = choosed['publish_time']
    thumbnail = Thumbnail(choosed['thumbnails'][-1], choosed['id'])
    author = choosed['channel']
    markup = Markup([
        [
            Button('- Upload To Telegram -', callback_data = f'download {choosed["id"]} {callback.message.reply_markup.inline_keyboard[0][0].callback_data.split()[-1]}'),
        ],
        [
            Button('- Previous -', callback_data = f'pre {int(index) + 1} {keyword}'),
            Button('- Next -' if callback_data != 'nothing' else '- Last Result -', callback_data = callback_data)
        ],
        [
            Button('- YouTube -', url = yturl)
        ]
    ])
    caption = f'- Title : {title}\n\n- Duration : {duration}\n\n- Views : {views.replace("مشاهدة", "view")}\n\n- Publish Since: {publish_time}\n\n- channel : {author}'
    await callback.message.edit_media(
        media = InputMediaPhoto(thumbnail, caption),
        reply_markup = markup
    )
    

@app.on_callback_query(filters.regex(r'^(pre)'))
async def _next(_: Client , callback: CallbackQuery):
    data = callback.data.split(maxsplit=2)[1:]
    index = data[0]
    keyword = data[1]
    await callback.answer('- Please, Wait a Moment..!', cache_time = 5)
    results = json.loads(Search(keyword))
    callback_data = f'next {int(index) - 1} {keyword}'
    choosed = results[int(index) - 1]
    yturl = url_prefix + choosed['url_suffix']
    title = choosed['title']
    duration = choosed['duration']
    views = choosed['views']
    publish_time = choosed['publish_time']
    thumbnail = Thumbnail(choosed['thumbnails'][-1], choosed['id'])
    author = choosed['channel']
    markup = Markup([
        [
            Button('- Upload To Telegram -', callback_data = f'download {choosed["id"]} {callback.message.reply_markup.inline_keyboard[0][0].callback_data.split()[-1]}'),
        ],
        [
            Button('- Previous -' if int(index) - 1 != 0 else '- First Result -', callback_data = f'pre {int(index) - 1} {keyword}' if int(index) - 1 != 0 else 'nothing'),
            Button('- Next -', callback_data = callback_data)
        ],
        [
            Button('- YouTube -', url = yturl)
        ]
    ])
    caption = f'- Title : {title}\n\n- Duration : {duration}\n\n- Views : {views.replace("مشاهدة", "view")}\n\n- Publish Since: {publish_time}\n\n- channel : {author}'
    await callback.message.edit_media(
        media = InputMediaPhoto(thumbnail, caption),
        reply_markup = markup
    )


async def downloadURL(message ,url, _type):
    wait_msg = await message.reply(emoji.MAGNIFYING_GLASS_TILTED_RIGHT)
    try:result = json.loads(Fetch(url))
    except yt_dlp.utils.DownloadError:return await message.reply('- Invalid URL!', reply_to_message_id = message.id)
    _id = result['id']
    title = result['title']
    try:thumbnail = Thumbnail(result['thumbnail'], _id)
    except:thumbnail = 'default.png'
    views = '{:,}'.format(result['view_count'])
    duration = result['duration_string']
    channel = result['channel']
    followers = '{:,}'.format(result['channel_follower_count'])
    publish_date = str(datetime.strptime(result['upload_date'], '%Y%m%d')).split()[0]
    icaption = f'- Title : {title}\n\n- Duration : {duration}\n\n- Views : {views} view\n\n- Published At : {publish_date}\n\n'
    icaption += f'- Channel : {channel}\n\n- Subscribers : {followers}\n```NOTE\nDOWNLOADING...```'    
    info_msg = await message.reply_photo(
        photo = thumbnail,
        caption = icaption,
        reply_to_message_id = message.id
    )
    await wait_msg.delete()
    wait_msg = await message.reply('- Preparing For Downloading...', reply_to_message_id = info_msg.id)
    embed = FetchLink(url, 'audio' if _type == 'a' else 'video')
    path = f'./{_id + ".mp4" if _type == "v" else _id + ".mp3"}'
    obj = SmartDL(embed, path, progress_bar=False)
    obj.start(blocking=False)
    while not obj.isFinished():
        caption = "- Speed: %s" % obj.get_speed(human=True)
        caption += "\n- Downloaded: %s" % obj.get_dl_size(human=True)
        caption += "\n- Eta: %s" % obj.get_eta(human=True)
        caption += "\n- Progress: %d%%" % (obj.get_progress()*100)
        caption += "\n- Status: %s" % obj.get_status()
        markup = Markup([[Button(("%s" % obj.get_progress_bar()).replace('#', '➖️'), callback_data='nothing')]])
        await wait_msg.edit_text(caption, reply_markup = markup)
        await sleep(3)
    if obj.isSuccessful():
        await wait_msg.edit_text('- Uploading...')
        func = InputMediaVideo if _type == 'v' else InputMediaAudio 
        await info_msg.edit_media(media = func(media = path ,caption = icaption.replace('```NOTE\nDOWNLOADING...```', f'\n\n- DOWNLOADED BY: @{app.me.username}')))
        caption = "-Uploaded.\n- Download task took %s" % obj.get_dl_time(human=True)
        await wait_msg.edit_text(caption)
    else: await wait_msg.edit_text('- An Error Has Been Occcured!')
    try:os.remove(path)
    except:...

def Thumbnail(url, _id):
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(f'./{_id}.png', 'wb') as f:
           for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return f'./{_id}.png'
    
if __name__ == '__main__': app.run()    
# 𝗪𝗥𝗜𝗧𝗧𝗘𝗡 𝗕𝗬 : @BENN_DEV
# 𝗦𝗢𝗨𝗥𝗖𝗘 : @BENfiles