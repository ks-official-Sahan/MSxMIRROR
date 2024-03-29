from os import remove as osremove, path as ospath, mkdir
from sys import prefix
from PIL import Image
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from time import sleep, time
from functools import partial
from datetime import datetime
from html import escape
from telegram import ParseMode
from threading import Thread

from bot import bot, user_data, dispatcher, LOGGER, config_dict, DATABASE_URL, OWNER_ID
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage, sendPhoto
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.db_handler import DbManger
from bot.helper.ext_utils.bot_utils import update_user_ldata, is_paid, is_sudo, get_readable_file_size, getUserTDs, getdailytasks
#from bot.helper.themes import BotTheme

handler_dict = {}
example_dict = {'prefix':'1. <code>@ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ ᴏʀ ᴀɴʏᴛʜɪɴɢ</code>', 
                'mprefix':'1. <code>@ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ ᴏʀ ᴀɴʏᴛʜɪɴɢ</code>', 
                'suffix':'1. <code>~ ᴏᴍɢ</code>\n2. <code>~ @ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ</code>', 
                'msuffix':'1. <code>~ ᴏᴍɢ</code>\n2. <code>~ @ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ</code>', 
                'caption':'`<b>{filename}\n\n➠Fast Download Link :\nshortner</b>`',
                'userlog':'<code>-100xxxxxx or Channel ID</code>',
                'ssite': '<b>sᴇɴᴅ sɪᴛᴇ ʟɪɴᴋ ʟɪᴋᴇ <code>kpslink.in</code>\n\n📌 sᴇᴛ ʏᴏᴜʀ sɪᴛᴇ ʟɪɴᴋ</b>',
                'sapi': '<b>sᴇɴᴅ sɪᴛᴇ ᴀᴘɪ ɪᴅ - <code>a33ce12542055ff79361d9bcc681ece612bdcaf8</code>\n\n📌 sᴇᴛ ʏᴏᴜʀ sɪᴛᴇ ᴀᴘɪ ɪᴅ</b>',
                'usertd':'1. <code>UserTD_Name 1TSYgS-88SkhkSuoS-KHSi7%^&s9HKj https://1.xyz.workers.dev/0:/Leecher</code>\n<b> Do not forget to add '+config_dict['SA_MAIL']+' to your TD as Content Manager</b>',
                'remname':'<b>Syntax:</b> previousname:newname:times|previousname:newname:times\n\n1. Fork:Star|Here:Now:1|WZML\n\n<b>Output :</b> Star Now : Click Here.txt', 
                'mremname':'<b>Syntax:</b> previousname:newname:times|previousname:newname:times\n\n1. Fork:Star|Here:Now:1|WZML\n\n<b>Output :</b> Star Now : Click Here.txt', 
                'imdb_temp':'Check all available fillings options <a href="">HERE</a> and Make Custom Template.', 
                'ani_temp':'Check all available fillings options <a href="">HERE</a> and Make Custom AniList Template.',
                'split_size':'In Normal Data Values like 2GB, 1GB, 500mB, 1.5 Gb\nNote: When Specific Data Type Given given like kb, gb, Only Mention in 2 Letters',
                'yt_ql': f'''1. <code>{escape('bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]')}</code> this will give 1080p-mp4.\n2. <code>{escape('bv*[height<=720][ext=webm]+ba/b[height<=720]')}</code> this will give 720p-webm.\nCheck all available qualities options <a href="https://github.com/yt-dlp/yt-dlp#filtering-formats">HERE</a>.'''
               }
fname_dict = {'prefix': 'Leech Prefix', 
            'mprefix':'Mirror Prefix', 
            'suffix':'Leech Suffix', 
            'msuffix':'Mirror Suffix', 
            'caption': 'Caption', 
            'userlog':'UserLog',
            'ssite': 'Shortner Site Link',
            'sapi': 'Shortner Site API',
            'usertd':'UserTD', 
            'remname':'Leech Remname', 
            'mremname':'Mirror Remname', 
            'imdb_temp':'IMDB Template', 
            'ani_temp':'Anime Template',
            'split_size':'TG Split Size',
            'yt_ql': 'YT-DLP Quality'
            }

def get_user_settings(from_user, key=None):
    user_id = from_user.id
    name = from_user.full_name
    #name = from_user.mention(style="html")
    buttons = ButtonMaker()
    thumbpath = f"Thumbnails/{user_id}.jpg"
    user_dict = user_data.get(user_id, False)
    if not user_dict:
        update_user_ldata(user_id, 'ubot_pm', config_dict['BOT_PM'])
    uplan = "Paid User" if is_paid(user_id) else "Normal User"
    if key is None:
        buttons.sbutton("ᴜɴɪᴠᴇʀsᴀʟ sᴇᴛᴛɪɴɢs", f"userset {user_id} universal")
        buttons.sbutton("ᴍɪʀʀᴏʀ sᴇᴛᴛɪɴɢs", f"userset {user_id} mirror")
        buttons.sbutton("ʟᴇᴇᴄʜ sᴇᴛᴛɪɴɢs", f"userset {user_id} leech")
        buttons.sbutton("sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs", f"userset {user_id} hari")
        buttons.sbutton("✘ ᴄʟᴏsᴇ ✘", f"userset {user_id} close")
        text = "<b><u>🥀 ᴜsᴇʀ sᴇᴛᴛɪɴɢs 📌</u></b>"
        #text = BotTheme('USER_SETTING', NAME=name, ID=user_id, USERNAME=f'@{from_user.username}', LANG=from_user.language_code, DC=from_user.dc_id)
        button = buttons.build_menu(1)
    elif key == 'universal':
        imdb = user_dict['imdb_temp'] if user_dict and user_dict.get('imdb_temp') else "Not Exists"
        anilist = user_dict['ani_temp'] if user_dict and user_dict.get('ani_temp') else "Not Exists"
        ytq = user_dict['yt_ql'] if user_dict and user_dict.get('yt_ql') else config_dict['YT_DLP_QUALITY'] if config_dict['YT_DLP_QUALITY'] else "Not Exists"
        ulist = user_dict['ulist_typ'] if user_dict and user_dict.get('ulist_typ') else f'{config_dict["LIST_MODE"].lower().capitalize()} (Default)'
        dailytl = config_dict['DAILY_TASK_LIMIT'] if config_dict['DAILY_TASK_LIMIT'] else "Unlimited"
        dailytas = user_dict.get('dly_tasks')[1] if user_dict and user_dict.get('dly_tasks') and user_id != OWNER_ID and not is_sudo(user_id) and not is_paid(user_id) and config_dict['DAILY_TASK_LIMIT'] else config_dict.get('DAILY_TASK_LIMIT', "Unlimited") if user_id != OWNER_ID and not is_sudo(user_id) and not is_paid(user_id) else "Unlimited"        
        
        if user_dict and user_dict.get('dly_tasks'):
            t = str(datetime.now() - user_dict['dly_tasks'][0]).split(':')
            lastused = f"{t[0]}h {t[1]}m {t[2].split('.')[0]}s ago"
        else: lastused = "Bot Not Used"

        buttxt = "ᴄʜᴀɴɢᴇ ʏᴛ-ᴅʟᴘ" if ytq != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ʏᴛ-ᴅʟᴘ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal yt_ql universal")
        buttxt = "ᴄʜᴀɴɢᴇ ʟɪsᴛ" if ulist != f'{config_dict["LIST_MODE"].lower().capitalize()} (Default)' else "sᴇᴛ ʟɪsᴛ"
        buttons.sbutton(buttxt, f"userset {user_id} setulist universal")

        if not config_dict['FORCE_BOT_PM']:
            if user_dict and user_dict.get('ubot_pm'):
                ubotpm = "Enabled"
                buttons.sbutton("ᴅɪsᴀʙʟᴇ ᴜsᴇʀ ᴘᴍ", f"userset {user_id} ubotoff")
            else:
                ubotpm = "Disabled"
                buttons.sbutton("ᴇɴᴀʙʟᴇ ᴜsᴇʀ ᴘᴍ", f"userset {user_id} uboton")
        else:
            ubotpm = "Force Enabled By Owner"
            buttons.sbutton("ᴅɪsᴀʙʟᴇ ᴜsᴇʀ ᴘᴍ", f"userset {user_id} ubotdisable")

        imdbval, anival = '', ''
        if imdb != "ɴᴏᴛ ᴇxɪsᴛs":
            imdbval = "ᴇxɪsᴛs"
            buttons.sbutton("ᴄʜᴀɴɢᴇ ɪᴍᴅʙ", f"userset {user_id} suniversal imdb_temp universal")
            buttons.sbutton("sʜᴏᴡ ɪᴍᴅʙ", f"userset {user_id} showimdb")
        else: buttons.sbutton("sᴇᴛ ɪᴍᴅʙ", f"userset {user_id} suniversal imdb_temp universal")
        if anilist != "ɴᴏᴛ ᴇxɪsᴛs":
            anival = "ᴇxɪsᴛs"
            buttons.sbutton("ᴄʜᴀɴɢᴇ ᴀɴɪ-ʟɪsᴛ", f"userset {user_id} suniversal ani_temp universal")
            buttons.sbutton("sʜᴏᴡ ᴀɴɪ-ʟɪsᴛ", f"userset {user_id} showanilist")
        else:
            buttons.sbutton("sᴇᴛ ᴀɴɪ-ʟɪsᴛ", f"userset {user_id} suniversal ani_temp universal")
        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} mback", 'footer')
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close", 'footer')
        button = buttons.build_menu(2)
        text = f'''<u>🥀 ᴜɴɪᴠᴇʀsᴀʟ sᴇᴛᴛɪɴɢs ғᴏʀ ⚙️<a href='tg://user?id={user_id}'>{name}</a></u>

<b>ʏᴛ-ᴅʟᴘ ǫᴜᴀʟɪᴛʏ</b> : <code>{escape(ytq)}</code>
<b>ᴅᴀɪʟʏ ᴛᴀsᴋs</b> : <code>{dailytas} / {dailytl} per day</code>
<b>ʟᴀsᴛ ʙᴏᴛ ᴜsᴇᴅ</b> : <code>{lastused}</code>
<b>ᴜsᴇʀ ʙᴏᴛ ᴘᴍ</b> : <code>{ubotpm}</code>
<b>ʟɪsᴛ ᴛʏᴘᴇ</b> : <code>{ulist}</code>
<b>ɪᴍᴅʙ</b> : <code>{imdbval if imdbval else imdb}</code>
<b>ᴀɴɪʟɪsᴛ</b> : <code>{anival if anival else anilist}</code>
'''
    elif key == 'mirror':
        prefix = user_dict['mprefix'] if user_dict and user_dict.get('mprefix') else "ɴᴏᴛ ᴇxɪsᴛs"
        suffix = user_dict['msuffix'] if user_dict and user_dict.get('msuffix') else "ɴᴏᴛ ᴇxɪsᴛs"
        remname = user_dict['mremname'] if user_dict and user_dict.get('mremname') else "ɴᴏᴛ ᴇxɪsᴛs"
        if user_dict and user_dict.get('usertd'):
            usertd = user_dict['usertd']
            GDrive, _, _ = getUserTDs(user_id, force=True)
        else: usertd = "ɴᴏᴛ ᴇxɪsᴛs"
        dailytlup = get_readable_file_size(config_dict['DAILY_MIRROR_LIMIT'] * 1024**3) if config_dict['DAILY_MIRROR_LIMIT'] else "Unlimited"
        dailyup = get_readable_file_size(getdailytasks(user_id, check_mirror=True)) if config_dict['DAILY_MIRROR_LIMIT'] and user_id != OWNER_ID and not is_sudo(user_id) and not is_paid(user_id) else "Unlimited"

        buttxt = "ᴄʜᴀɴɢᴇ ᴘʀᴇғɪx" if prefix != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ᴘʀᴇғɪx"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal mprefix mirror")
        buttxt = "ᴄʜᴀɴɢᴇ sᴜғғɪx" if suffix != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ sᴜғғɪx"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal msuffix mirror")
        buttxt = "ᴄʜᴀɴɢᴇ ʀᴇᴍɴᴀᴍᴇ" if remname != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ʀᴇᴍɴᴀᴍᴇ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal mremname mirror")
        
        if config_dict['ENABLE_USR_TD']:
            if user_dict and user_dict.get('usertd'):
                if user_dict.get('is_usertd'):
                    usertdstatus = "Enabled"
                    buttons.sbutton("ᴅɪsᴀʙʟᴇ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} usertdxoff")
                else:
                    usertdstatus = "Disabled"
                    buttons.sbutton("ᴇɴᴀʙʟᴇ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} usertdxon")
            else:
                usertdstatus = "Disabled"
                buttons.sbutton("ᴇɴᴀʙʟᴇ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} usertdxnotset")
        else:
            usertdstatus = "ᴜsᴇʀ ᴛᴅ ғᴇᴀᴛᴜʀᴇ ᴅɪꜱᴀʙʟᴇᴅ ʙʏ ᴏᴡɴᴇʀ !!!"
            buttons.sbutton("ᴇɴᴀʙʟᴇ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} usertdxdisable")
        usertds = ''
        if usertd != "ɴᴏᴛ ᴇxɪsᴛs":
            usertds = f"ᴇxɪsᴛs (ᴛᴏᴛᴀʟ : {len(GDrive)})"
            if config_dict['ENABLE_USR_TD']:
              buttons.sbutton("ᴄʜᴀɴɢᴇ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} suniversal usertd mirror")
            else:
              buttons.sbutton("ᴄʜᴀɴɢᴇ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} usertdxdisable")  
            buttons.sbutton("sʜᴏᴡ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} showusertds")
        else:
            if config_dict['ENABLE_USR_TD']:
              buttons.sbutton("sᴇᴛ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} suniversal usertd mirror")
            else:
              buttons.sbutton("sᴇᴛ ᴜsᴇʀ ᴛᴅ", f"userset {user_id} usertdxdisable")

        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} mback", 'footer')
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close", 'footer')
        button = buttons.build_menu(2)
        text = f'''<b><u>ᴍɪʀʀᴏʀ ᴀɴᴅ ᴄʟᴏɴᴇ sᴇᴛᴛɪɴɢꜱ ғᴏʀ <a href='tg://user?id={user_id}'>{name}</a></u></b>

<b>ᴘʀᴇғɪx</b> : <code>{escape(prefix)}</code>
<b>sᴜғғɪx</b> : <code>{suffix}</code>
<b>ᴜsᴇʀ ᴛᴅ ᴍᴏᴅᴇ</b> : <code>{usertdstatus}</code>
<b>ᴜᴀᴇʀ ᴛᴇᴀᴍ-ᴅʀɪᴠᴇ (s)</b> : <code>{usertds if usertds else usertd}</code>
<b>ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ</b> : <code>{dailyup} / {dailytlup} per day</code>
<b>ʀᴇᴍɴᴀᴍᴇ</b> : <code>{escape(remname)}</code>
'''
    elif key == 'hari':
        caption = user_dict['caption'] if user_dict and user_dict.get('caption') else "ɴᴏᴛ ᴇxɪsᴛs"
        cfont = user_dict['cfont'][0] if user_dict and user_dict.get('cfont') else "<code>ɴᴏᴛ ᴇxɪsᴛs</code>"
        ssite = user_dict['ssite'] if user_dict and user_dict.get('ssite') else "ɴᴏᴛ ᴇxɪsᴛs"
        sapi = user_dict['sapi'] if user_dict and user_dict.get('sapi') else "ɴᴏᴛ ᴇxɪsᴛs"

        buttxt = "ᴄʜᴀɴɢᴇ ᴜʀʟ-sɪᴛᴇ" if ssite != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ᴜʀʟ-sɪᴛᴇ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal ssite hari")
        buttxt = "ᴄʜᴀɴɢᴇ ᴜʀʟ-ᴀᴘɪ" if sapi != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ᴜʀʟ-ᴀᴘɪ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal sapi hari")
        buttxt = "ᴄʜᴀɴɢᴇ ᴄᴀᴘᴛɪᴏɴ" if caption != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ᴄᴀᴘᴛɪᴏɴ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal caption hari")
        #buttons.sbutton(buttxt, f"userset {user_id} suniversal cfont hari")
        if cfont != "<code>ɴᴏᴛ ᴇxɪsᴛs</code>": buttons.sbutton("ʀᴇᴍᴏᴠᴇ ᴄᴀᴘғᴏɴᴛ", f"userset {user_id} cfont")      

        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} mback", 'footer')
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close", 'footer')
        button = buttons.build_menu(2)
        text = f'''<b><u>🥀 sʜᴏʀᴛɴᴇʀ sᴇᴛᴛɪɴɢs ғᴏʀ ✨<a href='tg://user?id={user_id}'>{name}</a></u></b>

<b>sʜᴏʀᴛɴᴇʀ sɪᴛᴇ</b> : <code>{ssite}</code>
<b>sʜᴏʀᴛɴᴇʀ ᴀᴘɪ</b> : <code>{sapi}</code>
<b>ᴄᴀᴘᴛɪᴏɴ</b> : <code>{escape(caption)}</code>
<b>ᴄᴀᴘ ғᴏɴᴛ</b> : <code>{cfont}</code>
'''
    elif key == 'leech':
        prefix = user_dict['prefix'] if user_dict and user_dict.get('prefix') else "ɴᴏᴛ ᴇxɪsᴛs"
        suffix = user_dict['suffix'] if user_dict and user_dict.get('suffix') else "ɴᴏᴛ ᴇxɪsᴛs"
        caption = user_dict['caption'] if user_dict and user_dict.get('caption') else "ɴᴏᴛ ᴇxɪsᴛs"
        remname = user_dict['remname'] if user_dict and user_dict.get('remname') else "ɴᴏᴛ ᴇxɪsᴛs"
        cfont = user_dict['cfont'][0] if user_dict and user_dict.get('cfont') else "<code>ɴᴏᴛ ᴇxɪsᴛs</code>"
        userlog = user_dict['userlog'] if user_dict and user_dict.get('userlog') else "ɴᴏᴛ ᴇxɪsᴛs"
        ssite = user_dict['ssite'] if user_dict and user_dict.get('ssite') else "ɴᴏᴛ ᴇxɪsᴛs"
        sapi = user_dict['sapi'] if user_dict and user_dict.get('sapi') else "ɴᴏᴛ ᴇxɪsᴛs"
        dailytlle = get_readable_file_size(config_dict['DAILY_LEECH_LIMIT'] * 1024**3) if config_dict['DAILY_LEECH_LIMIT'] else "Unlimited"
        dailyll = get_readable_file_size(getdailytasks(user_id, check_leech=True)) if config_dict['DAILY_LEECH_LIMIT'] and user_id != OWNER_ID and not is_sudo(user_id) and not is_paid(user_id) else "Unlimited"
        lsplit = get_readable_file_size(user_dict['split_size']) if user_dict and user_dict.get('split_size') else get_readable_file_size(config_dict['TG_SPLIT_SIZE']) + "(Default)"

        if not user_dict and config_dict['AS_DOCUMENT'] or user_dict and user_dict.get('as_doc'):
            ltype = "ᴅᴏᴄᴜᴍᴇɴᴛ"
            buttons.sbutton("sᴇɴᴅ ᴀᴅ ᴍᴇᴅɪᴀ", f"userset {user_id} med")
        else:
            ltype = "ᴍᴇᴅɪᴀ"
            buttons.sbutton("sᴇɴᴅ ᴀᴅ ᴅᴏᴄᴜᴍᴇɴᴛ", f"userset {user_id} doc")

        if ospath.exists(thumbpath):
            thumbmsg = "ᴇxɪsᴛs"
            buttons.sbutton("ᴄʜᴀɴɢᴇ ᴛʜᴜᴍʙɴᴀɪʟ", f"userset {user_id} sthumb leech")
            #buttons.sbutton("sʜᴏᴡ ᴛʜᴜᴍʙɴᴀɪʟ", f"userset {user_id} showthumb")
        else:
            thumbmsg = "ɴᴏᴛ ᴇxɪsᴛs"
            buttons.sbutton("sᴇᴛ ᴛʜᴜᴍʙɴᴀɪʟ", f"userset {user_id} sthumb leech")

        esplits = 'ᴇɴᴀʙʟᴇᴅ' if not user_dict and config_dict['EQUAL_SPLITS'] or user_dict and user_dict.get('equal_splits') else 'ᴅɪsᴀʙʟᴇᴅ'

        buttxt = "ᴄʜᴀɴɢᴇ ᴜsᴇʀʟᴏɢ" if userlog != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ᴜsᴇʀʟᴏɢ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal userlog leech")
        buttxt = "ᴄʜᴀɴɢᴇ ᴘʀᴇғɪx" if prefix != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ᴘʀᴇғɪx"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal prefix leech")
        buttxt = "ᴄʜᴀɴɢᴇ sᴜғғɪx" if suffix != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ sᴜғғɪx"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal suffix leech")
        buttxt = "ᴄʜᴀɴɢᴇ ʀᴇᴍɴᴀᴍᴇ" if remname != "ɴᴏᴛ ᴇxɪsᴛs" else "sᴇᴛ ʀᴇᴍɴᴀᴍᴇ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal remname leech")
        buttxt = "ᴄʜᴀɴɢᴇ ʟᴇᴇᴄʜ-sᴘʟɪᴛ" if lsplit != get_readable_file_size(config_dict['TG_SPLIT_SIZE']) + "(Default)" else "sᴇᴛ ʟᴇᴇᴄʜ-sᴘʟɪᴛ"
        buttons.sbutton(buttxt, f"userset {user_id} suniversal split_size leech")
        
        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} mback", 'footer')
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close", 'footer')
        button = buttons.build_menu(2)
        text = f'''<b><u>🥀 ʟᴇᴇᴄʜ sᴇᴛᴛɪɴɢs ғᴏʀ ⚙️<a href='tg://user?id={user_id}'>{name}</a></u></b>

<b>ʟᴇᴇᴄʜ ᴛʏᴘᴇ</b> : <code>{ltype}</code>
<b>ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ</b> : <code>{thumbmsg}</code>
<b>ᴜsᴇʀ ʟᴏɢ</b> : <code>{userlog}</code>
<b>ᴘʀᴇғɪx</b> : <code>{escape(prefix)}</code>
<b>sᴜғғɪx</b> : <code>{suffix}</code>
<b>ʟᴇᴇᴄʜ sᴘʟɪᴛ sɪᴢᴇ</b> : <code>{lsplit}</code>
<b>ᴇǫᴜᴀʟ sᴘʟɪᴛ</b> : <code>{esplits}</code>
<b>ᴅᴀɪʟʏ ʟᴇᴇᴄʜ</b> : <code>{dailyll} / {dailytlle} per day</code>
<b>ʀᴇᴍɴᴀᴍᴇ</b> : <code>{escape(remname)}</code>
'''
    if uplan == "Paid User" and key:
        ex_date = user_dict.get('expiry_date', False)
        if not ex_date: ex_date = 'Not Specified'
        text += f"<b>ᴜsᴇʀ ᴘʟᴀɴ</b> : <code>{uplan}</code>\n"
        text += f"<b>ᴇxᴘɪʀʏ ᴅᴀᴛᴇ</b> : <code>{ex_date}</code>"
    elif key: text += f"<b>ᴜsᴇʀ ᴘʟᴀɴ</b> : <code>{uplan}</code>>"
    return text, button
    
def update_user_settings(message, from_user, key):
    msg, button = get_user_settings(from_user, key)
    editMessage(msg, message, button)

def user_settings(update, context):
    msg, button = get_user_settings(update.message.from_user)
    buttons_msg  = sendMessage(msg, context.bot, update.message, button)

def set_addons(update, context, data, omsg, key):
    message = update.message
    user_id = message.from_user.id
    handler_dict[user_id] = False
    value = message.text
    if data == 'split_size':
        sdic = ['b', 'kb', 'mb', 'gb', 'tb']
        value = value.strip()
        out = value[-2:].strip().lower()
        if out in sdic:
            value = int(value[:-2].strip().lower()) * 1024**sdic.index(out)
    update_user_ldata(user_id, data, value)
    update.message.delete()
    update_user_settings(omsg, message.from_user, key)
    if DATABASE_URL:
        DbManger().update_user_data(user_id)

def set_thumb(update, context, omsg):
    message = update.message
    user_id = message.from_user.id
    handler_dict[user_id] = False
    path = "Thumbnails/"
    if not ospath.isdir(path):
        mkdir(path)
    photo_dir = message.photo[-1].get_file().download()
    user_id = message.from_user.id
    des_dir = ospath.join(path, f'{user_id}.jpg')
    Image.open(photo_dir).convert("RGB").save(des_dir, "JPEG")
    osremove(photo_dir)
    update_user_ldata(user_id, 'thumb', des_dir)
    update.message.delete()
    update_user_settings(omsg, message.from_user, 'leech')
    if DATABASE_URL:
        DbManger().update_thumb(user_id, des_dir)

def edit_user_settings(update, context):
    query = update.callback_query
    message = query.message
    user_id = query.from_user.id
    data = query.data
    data = data.split()
    user_dict = user_data.get(user_id, False)
    if user_id != int(data[1]):
        query.answer(text="Not Yours!", show_alert=True)
    elif data[2] in ['universal', 'leech', 'mirror', 'hari']:
        query.answer()
        update_user_settings(message, query.from_user, data[2])
    elif data[2] == 'mback':
        query.answer()
        update_user_settings(message, query.from_user, None)
    elif data[2] == "doc":
        update_user_ldata(user_id, 'as_doc', True)
        query.answer(text="Your File Will Deliver As Document!", show_alert=True)
        update_user_settings(message, query.from_user, 'leech')
        if DATABASE_URL:
            DbManger().update_user_data(user_id)
    elif data[2] == "med":
        update_user_ldata(user_id, 'as_doc', False)
        query.answer(text="Your File Will Deliver As Media!", show_alert=True)
        update_user_settings(message, query.from_user, 'leech')
        if DATABASE_URL:
            DbManger().update_user_data(user_id)
    elif data[2] == 'esplits':
        query.answer()
        handler_dict[user_id] = False
        update_user_ldata(user_id, 'equal_splits', not bool(user_dict and user_dict.get('equal_splits')))
        update_user_settings(message, query.from_user, 'leech')
        if DATABASE_URL:
            DbManger().update_user_data(user_id)
    elif data[2] == "usertdxon":
        update_user_ldata(user_id, 'is_usertd', True)
        query.answer(text="Now, Your Files Will Be Mirrored/Cloned ON Your Personal TD!", show_alert=True)
        update_user_settings(message, query.from_user, 'mirror')
        if DATABASE_URL:
            DbManger().update_user_data(user_id)
    elif data[2] == "usertdxoff":
        update_user_ldata(user_id, 'is_usertd', False)
        query.answer(text="Now, Your Files Will Be Mirrorred/Cloned ON Global TD!", show_alert=True)
        update_user_settings(message, query.from_user, 'mirror')
        if DATABASE_URL:
            DbManger().update_user_data(user_id)
    elif data[2] == "usertdxnotset":
        query.answer(text="Set User TD First!", show_alert=True)
    elif data[2] == "usertdxdisable":
        query.answer(text="User TD Feature Disabled By Owner!", show_alert=True)
    elif data[2] == "uboton":
        update_user_ldata(user_id, 'ubot_pm', True)
        query.answer(text="Now, Your Files will be send to your PM!", show_alert=True)
        update_user_settings(message, query.from_user, 'universal')
        if DATABASE_URL:
            DbManger().update_user_data(user_id)
    elif data[2] == "ubotoff":
        update_user_ldata(user_id, 'ubot_pm', False)
        query.answer(text="Now, Your Files will not be send to your PM anymore!", show_alert=True)
        update_user_settings(message, query.from_user, 'universal')
        if DATABASE_URL:
            DbManger().update_user_data(user_id)
    elif data[2] == "ubotdisable":
        query.answer(text="Always BOT PM Mode is ON By Bot Owner!", show_alert=True)
    elif data[2] == "dthumb":
        handler_dict[user_id] = False
        path = f"Thumbnails/{user_id}.jpg"
        if ospath.lexists(path):
            query.answer(text="Thumbnail Removed!", show_alert=True)
            osremove(path)
            update_user_ldata(user_id, 'thumb', '')
            update_user_settings(message, query.from_user, 'leech')
            if DATABASE_URL:
                DbManger().update_thumb(user_id)
        else:
            query.answer(text="Old Settings", show_alert=True)
            update_user_settings(message, query.from_user, 'leech')
    elif data[2] == "sthumb":
        query.answer()
        if handler_dict.get(user_id):
            handler_dict[user_id] = False
            sleep(0.5)
        start_time = time()
        handler_dict[user_id] = True
        buttons = ButtonMaker()
        thumbpath = f"Thumbnails/{user_id}.jpg"
        if ospath.exists(thumbpath):
            buttons.sbutton("ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ᴘʜᴏᴛᴏ", f"userset {user_id} dthumb")
            buttons.sbutton("sʜᴏᴡ ᴛʜᴜᴍʙɴᴀɪʟ", f"userset {user_id} showthumb")
        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} back {data[3]}")
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close", 'footer')
        editMessage('sᴇɴᴅ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ ꜱᴀᴠᴇ ɪᴛ ᴀꜱ ᴄᴜꜱᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ.', message, buttons.build_menu(2))
        partial_fnc = partial(set_thumb, omsg=message)
        photo_handler = MessageHandler(filters=Filters.photo & Filters.chat(message.chat.id) & Filters.user(user_id),
                                       callback=partial_fnc)
        dispatcher.add_handler(photo_handler)
        while handler_dict[user_id]:
            if time() - start_time > 60:
                handler_dict[user_id] = False
                update_user_settings(message, query.from_user, 'leech')
        dispatcher.remove_handler(photo_handler)
    elif data[2] == 'back':
        query.answer()
        handler_dict[user_id] = False
        update_user_settings(message, query.from_user, data[3])
    elif data[2] == "showthumb":
        path = f"Thumbnails/{user_id}.jpg"
        if ospath.lexists(path):
            msg = f"Thumbnail for: {query.from_user.mention_html()} (<code>{str(user_id)}</code>)"
            delo = sendPhoto(text=msg, bot=context.bot, message=message, photo=open(path, 'rb'))
            Thread(args=(context.bot, update.message, delo)).start()
        else: query.answer(text="Send new settings command.")
    elif data[2] == "suniversal":
        if config_dict['PAID_SERVICE'] and user_id != OWNER_ID and not is_sudo(user_id) and not is_paid(user_id):
            query.answer("You not Not Paid User to Use this Feature. \n#Buy Paid Service", show_alert=True)
            return
        query.answer()
        if handler_dict.get(user_id):
            handler_dict[user_id] = False
            sleep(0.5)
        start_time = time()
        handler_dict[user_id] = True
        buttons = ButtonMaker()
        if data[3] == 'split_size':
            if not user_dict and config_dict['EQUAL_SPLITS'] or user_dict and user_dict.get('equal_splits'):
                buttons.sbutton("ᴅɪsᴀʙʟᴇ ᴇǫᴜᴀʟ sᴘʟɪᴛs", f"userset {user_id} esplits", 'header')
            else:
                buttons.sbutton("ᴇɴᴀʙʟᴇ ᴇǫᴜᴀʟ sᴘʟɪᴛs", f"userset {user_id} esplits", 'header')
        elif data[3] == 'caption':
            buttons.sbutton("sᴇᴛ ᴄᴜsᴛᴏᴍ ғᴏɴᴛ sᴛʏʟᴇ", f"userset {user_id} font hari", 'header')
        if user_dict and user_dict.get(data[3]):
            buttons.sbutton("ʀᴇᴍᴏᴠᴇ", f"userset {user_id} sremove {data[3]} {data[4]}")
        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} back {data[4]}")
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close", 'footer')
        #editMessage(f"<u>🥀 sᴇɴᴅ {fname_dict[data[3]]}'s ᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ.ᴛɪᴍᴇᴏᴜᴛ: 60sec</u>\n\nᴇxᴀᴍᴘʟᴇs:\n\n{example_dict[data[3]]}\n\n<b>ᴩᴏᴡᴇʀᴇᴅ ʙʏ - <a href=https://t.me/OMGxCLOUD>ᴏᴍɢ x ᴄʟᴏᴜᴅ</a></b>", message, buttons.build_menu(2))
        editMessage(f"<b><u>🥀 sᴇɴᴅ {fname_dict[data[3]]}'s ᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ.ᴛɪᴍᴇᴏᴜᴛ: 60sec</u>\n\nᴇxᴀᴍᴘʟᴇs </b>:\n\n{example_dict[data[3]]}", message, buttons.build_menu(2))
        partial_fnc = partial(set_addons, data=data[3], omsg=message, key=data[4])
        UNI_HANDLER = f"{data[3]}_handler"
        UNI_HANDLER = MessageHandler(filters=Filters.text & Filters.chat(message.chat.id) & Filters.user(user_id),
                                       callback=partial_fnc)
        dispatcher.add_handler(UNI_HANDLER)
        while handler_dict[user_id]:
            if time() - start_time > 60:
                handler_dict[user_id] = False
                update_user_settings(message, query.from_user, data[4])
        dispatcher.remove_handler(UNI_HANDLER)
    elif data[2] == "sremove":
        handler_dict[user_id] = False
        update_user_ldata(user_id, data[3], False)
        if DATABASE_URL: 
            DbManger().update_userval(user_id, data[3])
        query.answer(text=f"{fname_dict[data[3]]} Removed!", show_alert=True)
        update_user_settings(message, query.from_user, data[4])
    elif data[2] == "cfont":
        handler_dict[user_id] = False
        update_user_ldata(user_id, 'cfont', False)
        if DATABASE_URL: 
            DbManger().update_userval(user_id, 'cfont')
        query.answer(text="Caption Font Removed!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "font":
        query.answer()
        handler_dict[user_id] = False
        FONT_SPELL = {'b':'<b>Bold</b>', 'i':'<i>Italics</i>', 'code':'<code>Monospace</code>', 's':'<s>Strike</s>', 'u':'<u>Underline</u>', 'tg-spoiler':'<tg-spoiler>Spoiler</tg-spoiler>'}
        buttons = ButtonMaker()
        buttons.sbutton("sᴘᴏɪʟᴇʀ", f"userset {user_id} Spoiler")
        buttons.sbutton("ɪᴛᴀʟɪᴄs", f"userset {user_id} Italics")
        buttons.sbutton("ᴍᴏɴᴏsᴘᴀᴄᴇ", f"userset {user_id} Code")
        buttons.sbutton("sᴛʀɪᴋᴇ", f"userset {user_id} Strike")
        buttons.sbutton("ᴜɴᴅᴇʀ ʟɪɴᴇ", f"userset {user_id} Underline")
        buttons.sbutton("ʙʟᴏᴅ", f"userset {user_id} Bold")
        buttons.sbutton("ʀᴇɢᴜʟᴀʀ", f"userset {user_id} Regular")
        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} back {data[3]}")
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close")
        btns = buttons.build_menu(2)
        if user_dict and user_dict.get('cfont'): cf = user_data[user_id]['cfont']
        else: cf = [f'{FONT_SPELL[config_dict["CAPTION_FONT"]]} (Default)']
        editMessage("<u>Change your Font Style from below:</u>\n\n• Current Style : " + cf[0], message, btns)
    elif data[2] == "Spoiler":
        eVal = ["<tg-spoiler>Spoiler</tg-spoiler>", "tg-spoiler"]
        update_user_ldata(user_id, 'cfont', eVal)
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'cfont', eVal)
            LOGGER.info(f"User : {user_id} Font Style Saved in DB")
        query.answer(text="Font Style changed to Spoiler!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "Italics":
        eVal = ["<i>Italics</i>", "i"]
        update_user_ldata(user_id, 'cfont', eVal)
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'cfont', eVal)
            LOGGER.info(f"User : {user_id} Font Style Saved in DB")
        query.answer(text="Font Style changed to Italics!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "Code":
        eVal = ["<code>Monospace</code>", "code"]
        update_user_ldata(user_id, 'cfont', eVal)
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'cfont', eVal)
            LOGGER.info(f"User : {user_id} Font Style Saved in DB")
        query.answer(text="Font Style changed to Monospace!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "Strike":
        eVal = ["<s>Strike</s>", "s"]
        update_user_ldata(user_id, 'cfont', eVal)
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'cfont', eVal)
            LOGGER.info(f"User : {user_id} Font Style Saved in DB")
        query.answer(text="Font Style changed to Strike!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "Underline":
        eVal = ["<u>Underline</u>", "u"]
        update_user_ldata(user_id, 'cfont', eVal)
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'cfont', eVal)
            LOGGER.info(f"User : {user_id} Font Style Saved in DB")
        query.answer(text="Font Style changed to Underline!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "Bold":
        eVal = ["<b>Bold</b>", "b"]
        update_user_ldata(user_id, 'cfont', eVal)
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'cfont', eVal)
            LOGGER.info(f"User : {user_id} Font Style Saved in DB")
        query.answer(text="Font Style changed to Bold!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "Regular":
        eVal = ["Regular", "r"]
        update_user_ldata(user_id, 'cfont', eVal)
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'cfont', eVal)
            LOGGER.info(f"User : {user_id} Font Style Saved in DB")
        query.answer(text="Font Style changed to Regular!", show_alert=True)
        update_user_settings(message, query.from_user, 'hari')
    elif data[2] == "setulist":
        query.answer()
        handler_dict[user_id] = False
        buttons = ButtonMaker()
        buttons.sbutton("ʜᴛᴍʟ", f"userset {user_id} ulist HTML")
        buttons.sbutton("ᴛᴇʟᴇɢʀᴀᴘʜ", f"userset {user_id} ulist Telegraph")
        buttons.sbutton("ᴛᴇʟᴇɢʀᴀᴍ ᴅɪʀᴇᴄᴛ", f"userset {user_id} ulist Tele_Msg")
        buttons.sbutton("ʙᴀᴄᴋ", f"userset {user_id} back {data[3]}", "footer")
        buttons.sbutton("ᴄʟᴏsᴇ", f"userset {user_id} close", "footer")
        if user_id in user_data and user_data[user_id].get('ulist_typ'): ul = user_data[user_id]['ulist_typ']
        else: ul = f'{config_dict["LIST_MODE"].lower().capitalize()} (Default)'
        editMessage("<u>Change your List Fetch Mode from below:</u>\n\n• Current Mode : " + ul, message, buttons.build_menu(2))
    elif data[2] == "ulist":
        update_user_ldata(user_id, 'ulist_typ', data[3])
        if DATABASE_URL:
            DbManger().update_userval(user_id, 'ulist_typ', data[3])
            LOGGER.info(f"User : {user_id} List Mode Saved in DB")
        query.answer(text=f"List Mode Changed to {data[3]}!", show_alert=True)
        update_user_settings(message, query.from_user, 'universal')
    elif data[2] == "showimdb":
        if user_id not in user_data and not user_data[user_id].get('imdb_temp'):
            return query.answer(text="Send new settings command. 🙃")
        query.answer()
        imdb = user_data[user_id].get('imdb_temp')
        if imdb:
            msg = f"IMDB Template for: {query.from_user.mention_html()} (<code>{str(user_id)}</code>)\n\n{escape(imdb)}"
            im = sendMessage(msg, context.bot, message)
            Thread(args=(context.bot, update.message, im)).start()
    elif data[2] == "showanilist":
        if user_id not in user_data and not user_data[user_id].get('ani_temp'):
            return query.answer(text="Send new settings command. 🙃")
        query.answer()
        anilist = user_data[user_id].get('ani_temp')
        if anilist:
            msg = f"AniList Template for: {query.from_user.mention_html()} (<code>{str(user_id)}</code>)\n\n{escape(anilist)}"
            ani = sendMessage(msg, context.bot, message)
            Thread(args=(context.bot, update.message, ani)).start()
    elif data[2] == "showusertds":
       if user_id not in user_data and not user_data[user_id].get('usertd'):
            return query.answer(text="Old settings!")
       if user_dict and user_dict.get('usertd'):
           GNames, GIDs, GIndex = getUserTDs(user_id, force=True)
           msg = f"<b>User TDs Info :</b>\n\n"
           for i, _ in enumerate(GNames):
               msg += f"{i+1}. <i>Name :</i> {GNames[i]}\n"
               msg += f"   <i>GDrive ID :</i> <code>{GIDs[i]}</code>\n"
               msg += f"   <i>Index URL :</i> {GIndex[i] if GIndex[i] else 'Not Provided'}\n\n"
           try:
               bot.sendMessage(chat_id=user_id, text=msg, parse_mode=ParseMode.HTML)
               query.answer("UserTD details send in Private (PM) Successfully", show_alert=True)
           except: query.answer("Start the Bot in Private and Try Again to get your UserTD Details!", show_alert=True)
    else:
        query.answer()
        handler_dict[user_id] = False
        query.message.delete()
        query.message.reply_to_message.delete()

def send_users_settings(update, context):
    msg, auth_chat, sudos, leechlogs, linklogs, mirrorlogs = '', '', '', '', '', ''
    for u, d in user_data.items():
        try:
            for ud, dd in d.items():
                if ud == 'is_auth' and dd is True:
                    auth_chat += f"<b>{bot.get_chat(u).title}</b> ( <code>{u}</code> )\n"
                elif ud == 'is_sudo' and dd is True:
                    sudos += f"<a href='tg://user?id={u}'>{bot.get_chat(u).first_name}</a> ( <code>{u}</code> )\n"
        except:
            if u == 'is_leech_log':
                leechlogs = '\n'.join(f"<b>{bot.get_chat(ll).title}</b> ( <code>{ll}</code> )" for ll in d) + "\n"
            elif u == 'mirror_logs':
                mirrorlogs = '\n'.join(f"<b>{bot.get_chat(ll).title}</b> ( <code>{ll}</code> )" for ll in d) + "\n"
            elif u == 'link_logs':
                linklogs = '\n'.join(f"<b>{bot.get_chat(ll).title}</b> ( <code>{ll}</code> )" for ll in d) + "\n"
        else:
            continue
    msg = f'<b><u>Authorized Chats💬 :</u></b>\n{auth_chat}\n<b><u>Sudo Users👤 :</u></b>\n{sudos}\n<b><u>Leech Log:</u></b>\n{leechlogs}\n<b><u>Mirror Log♻️ :</u></b>\n{mirrorlogs}\n<b><u>Links Log🔗 :</u></b>\n{linklogs}'
    sendMessage(msg, context.bot, update.message)

def sendPaidDetails(update, context):
    paid = ''
    for u, d in user_data.items():
        try:
            for ud, dd in d.items():
                if ud == 'is_paid' and dd is True:
                    ex_date = user_data[u].get('expiry_date', False)
                    if not ex_date: ex_date = 'Not Specified'
                    paid += f"<a href='tg://user?id={u}'>{bot.get_chat(u).first_name}</a> ( <code>{u}</code> ) : {ex_date}\n"
                    break
        except: 
            continue
    if not paid: paid = 'No Data'
    sendMessage(f'<b><u>Paid Users🤑 :</u></b>\n\n{paid}', context.bot, update.message)


pdetails_handler = CommandHandler(command=BotCommands.PaidUsersCommand, callback=sendPaidDetails,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
users_settings_handler = CommandHandler(BotCommands.UsersCommand, send_users_settings,
                                            filters=CustomFilters.owner_filter | CustomFilters.sudo_user)
user_set_handler  = CommandHandler(BotCommands.UserSetCommand, user_settings,
                                   filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
but_set_handler = CallbackQueryHandler(edit_user_settings, pattern="userset")

dispatcher.add_handler(user_set_handler )
dispatcher.add_handler(but_set_handler)
dispatcher.add_handler(users_settings_handler)
dispatcher.add_handler(pdetails_handler)
