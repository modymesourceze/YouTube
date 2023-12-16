from pyrogram import Client as app, filters
from pyrogram import Client as temp
from pyrogram.types import InlineKeyboardButton as btn, InlineKeyboardMarkup as mk
import time
from kvsqlite.sync import Client as mody

db = mody("data.sqlite", 'fuck')

admins = db.get('admin_list')
@app.on_message(filters.private & filters.regex("^/start$"), group=1)
async def ade(app, msg):
    user_id = msg.from_user.id
    user_info = db.get(f'user_{user_id}')
    
    if user_id in admins:
        keys = mk(
            [
                [btn('اخر تحديثات البوت 🧬', url='https://t.me/UI_XB')],
                [btn('قسم تغيير الكلايش', 'set_start')],
                [btn('قسم الاشتراك الاجبارى', 'setforce'), btn('قسم الادمنية', 'admins_bot')],
                [btn('قسم الاذاعة', 'brods'), btn('قسم الاحصائيات', 'stats')],
                [btn('• اعدادات بوت الرشق •', 'setting_bot')],
                
            ]
        )
        await msg.reply("""**• اهلا بك في لوحه الأدمن الخاصه بالبوت 🤖**

- يمكنك التحكم في البوت الخاص بك من هنا \n\n===================""", reply_markup=keys)
@app.on_callback_query(filters.regex("^add_admin$"), group=6)
async def add_admin(app, query):
    user_id = query.from_user.id
    if user_id in admins:
        askk = await app.ask(user_id, 'يرجى إرسال معرف المستخدم لترقيته كمسؤول في البوت')
        if askk.text:
            try:
                t_id = int(askk.text)
            except ValueError:
                await askk.reply("يرجى إرسال معرف المستخدم بتنسيق صحيح")
                return
            if db.exists("admin_list"):
                s = db.get("admin_list")
                if t_id not in s:
                    s.append(t_id)
                    db.set('admin_list', s)
                else:
                    await askk.reply(f"المستخدم {t_id} مسؤول بالفعل")
                    return
            else:
                db.set("admin_list", [t_id])
            await askk.reply(f"تمت إضافة المستخدم {t_id} كمسؤول في البوت")
            return
        else:
            pass
@app.on_callback_query(filters.regex("^delete_admin$"), group=7)
async def ada_admin(app, query):
    user_id = query.from_user.id
    if user_id in admins:
        askk = await app.ask(user_id, 'ارسل الان ايدي الشخص لازالته من الادمنية')
        if askk.text:
            try:
                t_id = int(askk.text)
            except:
                await askk.reply("برجاء ارسل الايدي بشكل صحيح")
                return
            if db.exists("admin_list"):
                s = db.get("admin_list")
                s.remove(t_id)
                db.set('admin_list', s)
                await askk.reply(f"تم مسح : {t_id} من ادمنية البوت ")
                return
            else:
                db.set("admin_list", [])
                s = db.get("admin_list")
                s.append(t_id)
                db.set('admin_list', s)
                await askk.reply(f"تم مسح : {t_id} من ادمنية البوت ..")
                return
        else:
            pass

@app.on_callback_query(filters.regex("^stats$"))
async def statss(app, query):
    count = 0
    users = db.keys()
    x = "• معلومات البوت العامة 📊 :\n"
    for i in users:
        if "user_" in str(i[0]):
            count+=1
    x+=f'• عدد اعضاء البوت : {count} \n'
    for i in users:
        if "user_" in str(i[0]) and "gift" not in str(i[0]) or 'price_' not in str(i[0]) or 'sessions' not in str(i[0]):
            try:
                i = db.get(i[0])
                print(i)
                mon+=int(i['coins'])
            except:
                continue
    await app.send_message(query.from_user.id, x)
    return
@app.on_callback_query(filters.regex("^add_coins$"), group=8)
async def add_coinssw(app, query):
    user_id = query.from_user.id
    if user_id in admins:
        askk = await app.ask(user_id, 'ارسل الي دي العضو اللي تريد ترسله النقاط.')
        if askk.text:
            try:
                t_id = int(askk.text)
            except:
                await askk.reply("ارسل الايدي بشكل صحيح")
                return
            ask2 = await app.ask(user_id, 'ارسل عدد النقاط اللي تريد ارسالها للشخص')
            if ask2.text:
                try:
                    amount = float(ask2.text)
                except:
                    return
                b = db.get(f"user_{t_id}")
                b['coins'] = float(b['coins']) + amount
                db.set(f"user_{t_id}", b)
                await ask2.reply(f"• تم اضافة نقاط الي : `{t_id}`\n\n• العدد : `{amount}` ")
                await app.send_message(int(t_id), f"• تم اضافة `{amount}` نقاط الى حسابك من قبل المطور")
            else:
                pass
        else:
            pass
@app.on_callback_query(filters.regex("^less_coin$"), group=9)
async def les_co(app, query):
    user_id = query.from_user.id
    if user_id in admins:
        askk = await app.ask(user_id, 'ارسل اي دي العضو اللي تريد تخصم منه النقاط')
        if askk.text:
            try:
                t_id = int(askk.text)
            except:
                await askk.reply("رجاء ارسل الاي دي بشكل صحيح")
                return
            ask2 = await app.ask(user_id, 'ارسل عدد النقاط اللي تريد خصمة من هذا الشخص')
            if ask2.text:
                try:
                    amount = float(ask2.text)
                except:
                    return
                b = db.get(f"user_{t_id}")
                b['coins'] = float(b['coins']) - amount
                db.set(f"user_{t_id}", b)
                await ask2.reply(f"• تم خصم نقاط من : `{t_id}`\n\n• العدد : `{amount}` ")
                await app.send_message(int(t_id), f"• تم خصم `{amount}` نقاط من حسابك من قبل المطور")
                return
            else:
                pass
        else:
            pass
@app.on_callback_query(filters.regex("^brods$"), group=10)
async def brod_ss(app, query):
    user_id = query.from_user.id
    count = 0
    users = db.keys()
    for i in users:
        if "user_" in str(i[0]):
            try:
                count+=1
            except:
                continue
    ask1 = await app.ask(user_id, '• ارسل محتوى الاذاعة : \n\n•يمكنك ارسال : نص او ميديا او الخ')
    if ask1:
        c = 0
        msg_id = ask1.id
        k = db.keys()
        for i in k:
            if "user_" in str(i[0]) and "gift" not in str(i[0]) or 'price_' not in str(i[0]) or 'sessions' not in str(i[0]):
                try:
                    id = int(str(i[0]).replace("user_", ''))
                except:
                    continue
                try:
                    await app.copy_message(id, user_id, msg_id)
                    c+=1
                    await app.edit_message_text(user_id, ask1.request.id, f'• جاري الاذاعه الى `{count}` مستخدم 🌐\n\n• تم الارسال الى `{c}` مستخدم')
                except:
                    continue
        all = int(count) - int(c)
        await ask1.reply(f"• تم انتهاء الاذاعة بنجاح ✅:\n\n• عدد الاشخاص الذين شاهدو الاذاعة : {c}\n\n• المستخدمين الذين لم يستطع البوت ارسال اذاعه لهم {all} مستخدم",reply_markup=mk([[btn(text=f'رجوع',callback_data='hkajs')]]))
        await app.edit_message_text(user_id, ask1.request.id, f'• تم الارسال الى `{c}` مستخدم',reply_markup=mk([[btn(text=f'تم الانتهاء من الاذاعة',callback_data='hkajs')]]))
import datetime

def ttd(timestamp) -> str:
    
    date = datetime.datetime.fromtimestamp(timestamp)
    
    
    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_date
@app.on_callback_query(filters.regex("^get_infos$"), group=11)
async def get_infso(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل الان ايدي الشخص اللي تريد تعرف معلوماته')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("هذا الحساب غير موجود في البوت")
            return
        try:
            coins = d['coins']
            ddd = str(d['date']).split(".")[0]
            date = ttd(int(ddd))
        except Exception as x:
            print(x)
            return
        await ask.reply(f'• معلومات حسابه :\n\n• عدد نقاطه : {coins}\n\n• تاريخ دخولة للبوت : {date} ')
@app.on_callback_query(filters.regex("^ban_mes$"), group=12)
async def ban_mes(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل ايدي العضو لحظره من استخدام البوت')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("هذا العضو غير موجود داخل البوو")
            return
        if db.exists("ban_list"):
            dw = db.get("ban_list")
            dw.append(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم حظر العضو من استخدام البوت")
        else:
            db.set("ban_list", [])
            dw = db.get("ban_list")
            dw.append(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم حظر العضو من استخدام البوت")
@app.on_callback_query(filters.regex("^unban_mes$"), group=13)
async def unban_me(app, query):
    user_id = query.from_user.id
    ask = await app.ask(user_id, 'ارسل ايدي العضو اللي تريد حذفه من قائمة الحظر')
    if ask.text:
        try:
            id = int(ask.text)
        except:
            return
        d = db.get(f"user_{id}")
        if d is None:
            await ask.reply("الحساب غير موجود دخال البوت")
            return
        if db.exists("ban_list"):
            dw = db.get("ban_list")
            dw.remove(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم الغاء حظر العضو")
        else:
            db.set("ban_list", [])
            dw = db.get("ban_list")
            dw.remove(id)
            db.set(f"ban_list", dw)
            await ask.reply("تم الغاء حظر العضو")
@app.on_callback_query(filters.regex('^setforce$'))
async def setforcee(app, query):
    ask = await app.ask(
        query.from_user.id,
        'ارسل معرفات قنوات الاشتراك هكذا بمسافة بين كل معرف :\n\n@first @second .'
    )
    if ask.text:
        channels = ask.text.replace("@", '').split(' ')
        print(channels)
        db.set(f'force', channels)
        await ask.reply('تم تعيين القنوات بنجاح ..')
        return
