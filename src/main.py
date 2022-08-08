import discord
import os
import pandas as pd
import csv
from discord.ext import commands
import secrets2
import markovify
import re
import requests

def run_bot():
    text_models = {}
    secret = secrets2.get_discord_token()
    bot = commands.Bot(command_prefix='-')

    @bot.command(name='tell')
    async def tell(ctx):

        question = ctx.message.content.lstrip('-tell')
        app_id = secrets2.get_wa_appid()
        endpoint = 'https://api.wolframalpha.com/v1/result?appid=' +app_id + '&i=' +question

        r = requests.get(endpoint)

        await ctx.send(r.text)

    @bot.command(name='juuh')
    async def juuh(ctx):

        server_name = ctx.guild.name

        if server_name not in text_models.keys():

            df = pd.DataFrame()

            for entry in os.scandir('.'):
                if entry.is_file():
                    if '.csv' in entry.name[-4:]:
                        if server_name in entry.name and 'bot' not in entry.name:
            
                            if len(df) == 0:
                                df = pd.read_csv(entry.name)
                            else:
                                uusi = pd.read_csv(entry.name)
                                df = df.append(uusi)

            texti = ''
            rivi = ''

            for row in df['content'].dropna():
                rivi = re.sub('[<].*[>]', '', row)
                if len(rivi) > 10 and len(rivi) < 500:
                    texti = texti + str(rivi) + '\n'

            text_model = markovify.NewlineText(texti, state_size=2)

            text_models[server_name] = text_model

        lause = ''
        juuh_output = ''

        for i in range(10):

            uusi_lause = text_models[server_name].make_sentence(tries=100, min_words=10)

            if uusi_lause is None:
                uusi_lause = ''
      
            if len(uusi_lause)>len(lause):
                lause=uusi_lause

        await ctx.send(lause)

    @bot.command(name='update')
    async def update(ctx):

            text_models = {}
            guild = ctx.guild
            guild_name = guild.name

            for channel in guild.channels:

                data = []
                channel_name = channel.name

                try:
                    history = await channel.history(limit=50000).flatten() #5000

                    for message in history:
        
                        message_data = {'created_at':message.created_at,
                                        'author':message.author,
                                        'content':message.content}

                        data.append(message_data)

                    df = pd.DataFrame(data)
                    filename = guild_name + '_' + channel_name + '.csv'
                    df.to_csv(filename, index=False)     

                except:
                    pass

            await ctx.send('updated')
    
    @bot.event
    async def on_connect():
        print(f'{bot.user.name} has connected to Discord!')

    bot.run(secret)

if __name__ == "__main__":
    run_bot()
else:
    pass
