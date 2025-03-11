from pyrogram.errors import FloodWait,BadRequest
import pandas as pd
from datetime import date, datetime
import asyncio

# check if empty or exists

def validate_channels(app,channels):
    """ The function checks whether the channels in the list exist and public.     
    Input:

    channels(list) - a list of the names or ids of Telegram channels (["nytimes",...])

    Output:
    boolean list - green means a channel exists, yellow - a channel exists but private, red - a channel doesn't exist.
    """
    valid=[]
    with app:
        for channel in channels:
            try:
                info = app.get_chat(channel)
                if info.type.name == "CHANNEL":
                    valid.append("green")
                elif info.type.name == "PRIVATE":
                    valid.append("yellow")
            except BadRequest:
                valid.append('red')
    return valid



def get_posts_text(app, channel,keyword = "", date_from = [2000,1,1], date_to = False,path="", save_as = "xlsx"):
    """The function extracts messages/posts for a Telegram channel.

    Input: 

    - app(pyrogram.client.Client): application client
    - channel(str): name of a Telegram channel (https://t.me/....). 
    - keyword(str, optional): lowercase keyword to subset posts
    - date_from(list,optional): [YYYY,M,D] including
    - date_to(list,optional): [YYYY,M,D] including
    - path(str,optional): path where the dataset should be stored. If not defined, 
        the dataset is stored in the same folder where the executed code is located.
    - save_as(str,optional): (xlsx, json) defines the file type of the dataset to be stored

    Output:

    - a file (xlsx or json) stored in a path folder. The dataset consists of 5 columns: channel, message_id,forward_from, message_date, message_text

    """
    async def get_messages(channel): 
        try:
            async with app:
                df = pd.DataFrame(columns = ["channel","message_id","forward_from","message_date","message_text"])
                i=0
                if date_to:
                    date_to[2] = date_to[2]+ 1 
                    messages = app.get_chat_history(channel,offset_date = datetime(*date_to))
                        
                else:
                    messages = app.get_chat_history(channel)
           

                async for message in messages: 
                    if message.text: # check whether a message contains a main text
                        if (keyword in message.text.lower()) and (message.date.date() >= date(*date_from)): 
                            df.loc[i,:]=[channel, message.id,message.forward_from,message.date, message.text]
                            i+=1
                        else:
                            break
                    elif message.caption: # if a message doesn't contain a main text, 
                                            #it is highly likely that a message has a photo, and therefore, 
                                            # the main text is located in the message.caption object.
                        if (keyword in message.caption.lower()) and (message.date.date() >= date(*date_from)): 
                            df.loc[i,:]=[channel, message.id, message.forward_from,message.date, message.caption]
                            i+=1
                        else:
                            break                

            if save_as =="xlsx":
                df.to_excel(path+channel+".xlsx")
            elif save_as =="json":
                df.to_json(path+channel+".json")

        
        except BadRequest:
            print("!!! The Telegram channel does not exist. Please double-check the username of the channel !!!") 


    app.run(get_messages(channel))
   

def get_comments_from_channel(app, channel,keyword = "",date_from = [2000,1,1], date_to = False,path="", save_as = "xlsx"):
    """The function extracts comments under posts for a Telegram channel.

    Input: 

    - app(pyrogram.client.Client): application client
    - channel(str): name of a Telegram channel (https://t.me/....). 
    - keyword(str, optional): lowercase keyword to subset posts (if a keyword in the post, collect the comments)
    - date_from(list,optional): [YYYY,M,D] including
    - date_to(list,optional): [YYYY,M,D] including
    - path(str,optional): path where the dataset should be stored. If not defined, 
        the dataset is stored in the same folder where the executed code is located.
    - save_as(str,optional): (xlsx, json) defines the file type of the dataset to be stored

    Output:

    - a file (xlsx or json) stored in a path folder.

    """
    async def get_comments(channel):
        df = pd.DataFrame(columns=["channel","message_id","message_date","comment_date","comment_text"])
        i = 0
        try:
            async with app:
                if date_to:
                    date_to[2] = date_to[2] + 1 
                    messages = app.get_chat_history(channel,offset_date = datetime(*date_to))
                else:
                    messages = app.get_chat_history(channel)

                async for message in messages:
                    if message.text: # check whether a message contains a main text
                        if (keyword in message.text.lower()) and (message.date.date() >= date(*date_from)):
                            try:
                                async for comment in app.get_discussion_replies(channel, message.id):
                                    df.loc[i,:]=[channel, message.id, message.date, comment.date, comment.text]
                                    i+=1
                            except FloodWait as e:
                                await asyncio.sleep(e.value)
                            else:
                                continue
                        else:
                            break
                    elif message.caption:# if a message doesn't contain a main text, 
                                            #it is highly likely that a message has a photo, and therefore, 
                                            # the main text is located in the message.caption object.
                        if  (keyword in message.caption.lower()) and (message.date.date() >= date(*date_from)):
                            try:
                                async for comment in app.get_discussion_replies(channel, message.id):
                                    df.loc[i,:]=[channel, message.id, message.date, comment.date, comment.text]
                                    i+=1 
                            except FloodWait as e:
                                await asyncio.sleep(e.value)
                            else:
                                continue
                        else: 
                            break

            if save_as =="xlsx":
                df.to_excel(path+channel+"_comments.xlsx")
            elif save_as =="json":
                df.to_json(path+channel+"_comments.json")

        except BadRequest:
            print("!!! The Telegram channel does not exist. Please double-check the username of the channel !!!")



    app.run(get_comments(channel))
            
def get_comments_from_posts(app, channel, posts, path="", save_as = "xlsx"):
    """The function extracts comments under posts for a one Telegram channel.

    Input: 

    - app(pyrogram.client.Client): application client
    - channels(list): list of channels or a channel. 
        For example, ["channel1","channel2"] or ["channel1"] if you need data in only one channel. 
    - posts(list): list of messages id in a given channel
    - path(str,optional): path where the dataset should be stored. If not defined, 
        the dataset is stored in the same folder where the executed code is located.
    - save_as(str,optional): (xlsx, json) defines the file type of the dataset to be stored

    Output:

    - a file (xlsx or json) stored in a path folder.

    """
    async def get_comments():
        i=0
        df = pd.DataFrame(columns=["channel","message_id","comment_date","comment_text"])
        try:
            async with app:
                for message_id in posts:
                    try:
                        async for comment in app.get_discussion_replies(channel, message_id):
                            df.loc[i,:]=[channel, message_id, comment.date, comment.text]
                            i+=1
                    except FloodWait as e: # if too many requests, sleep
                        await asyncio.sleep(e.value)

            if save_as =="xlsx":
                df.to_excel(path+channel+"_comments.xlsx")
            elif save_as =="json":
                df.to_json(path+channel+"_comments.json")
        
        except BadRequest:
            print("!!! The post or Telegram channel do not exist. Please double-check the username of the channel or the message id!!!")
                    
    app.run(get_comments())
    

            
def get_reactions_from_channel(app, channel,keyword = "", date_from = [2000,1,1], date_to = False,path="", save_as = "xlsx"):
    """The function extracts reactions for a list of Telegram channels.

    Input: 

    - app(pyrogram.client.Client): application client
     - channel(str): name of a Telegram channel (https://t.me/....). 
    - keyword(str, optional): lowercase keyword to subset posts
    - date_from(list,optional): [YYYY,M,D] including
    - date_to(list,optional): [YYYY,M,D] including
    - path(str,optional): path where the dataset should be stored. If not defined, 
        the dataset is stored in the same folder where the executed code is located.
    - save_as(str,optional): (xlsx, json) defines the file type of the dataset to be stored

    Output:

    - a file (xlsx or json) stored in a path folder. The dataset consists of 6 columns: channel, message_id,forward__from, message_date, message_text, message_reactions
    """
    async def get_reactions(channel): 
        try:

            async with app:
                df = pd.DataFrame(columns = ["channel","message_id","forward_from","message_date","message_text","message_reactions"])
                i=0
                if date_to:
                    date_to[2] = date_to[2]+ 1 
                    messages = app.get_chat_history(channel,offset_date = datetime(*date_to))
                else:
                    messages = app.get_chat_history(channel)

                async for message in messages: 
                    if message.text: # check whether a message contains a main text
                        if (keyword in message.text.lower()) and (message.date.date() >= date(*date_from)): 
                            df.loc[i,:]=[channel, message.id,message.forward_from,message.date, message.text,message.reactions]
                            i+=1
                        else:
                            break
                    elif message.caption:# if a message doesn't contain a main text, 
                                            #it is highly likely that a message has a photo, and therefore, 
                                            # the main text is located in the message.caption object.
                        if (keyword in message.caption.lower()) and (message.date.date() >= date(*date_from)): 
                            df.loc[i,:]=[channel, message.id, message.forward_from,message.date, message.caption,message.reactions]
                            i+=1
                        else:
                            break
                
            def extract_reactions(pyrogram_dict):
                return {i.emoji: i.count for i in pyrogram_dict.reactions}
            try:
                df["message_reactions"] = df["message_reactions"].apply(extract_reactions)
            except:
                pass

            if save_as =="xlsx":
                df.to_excel(path+channel+"_reactions.xlsx")
            elif save_as =="json":
                df.to_json(path+channel+"_reactions.json")

        except BadRequest:
                    print("!!! The Telegram channel does not exist. Please double-check the username of the channel !!!")

    app.run(get_reactions(channel))




