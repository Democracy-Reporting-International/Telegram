from pyrogram import Client
import telegram_functions as tgf

# 1. Create a Telegram application. Details: https://core.telegram.org/api/obtaining_api_id

api_id =  # your api_id (8 digits)
api_hash = "" # your api_hash
app_name = "" # your api_name


app = Client(app_name, api_id=api_id, api_hash=api_hash)

lst=tgf.validate_channels(app, ['nytimes','nh','tratatata','redakciya_channel'])
print(lst)


# You will be asked to provide your phone number and a confirmation code sent via Telegram app.

#help(tgf.get_posts_text)

# Get text from posts on one Telegram channel
tgf.get_posts_text(app, channel = "nytimes",keyword = "",
                     date_from = [2022,12,1], date_to = [2022,12,12],
                     path="",save_as = "xlsx")

# Get comments under posts on one Telegram channel
tgf.get_comments_from_channel(app, channel = "margaritasimonyan",keyword = "",
                                date_from = [2023,1,8], date_to = [2023,1,10],
                                path="", save_as = "xlsx")

# Get comments under specific posts on one Telegram channel
tgf.get_comments_from_posts(app, channel = "margaritasimonyan",posts = [12571,12570],
                                path="", save_as = "xlsx")

# Get reactions to posts on one Telegram channel
tgf.get_reactions_from_channel(app, channel = "nytimes",keyword = "",
                     date_from = [2022,12,1], date_to = [2022,12,12],
                     path="",save_as = "xlsx")
