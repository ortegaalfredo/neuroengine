"""
#### 2-Clause BSD licence:

Copyright 2023 Alfredo Ortega @ortegaalfredo

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import discord
import os
import re
import sys
import time
import json
import threading
import http.client
from neuroengine import neuroengine
from discord.ext import commands,tasks

# Prompt needed for alpaca-type instruction LLMs
lora_prompt="""Below is an instruction that describes a task. Write a response that appropriately completes the request.
### Instruction:
%s
### Response:
"""
end_mark="### Response:"

# Log function
def log(str):
    a=open("log.txt","ab")
    a.write(str.encode())
    a.write('\n'.encode())
    a.close()

# Discord configuration
intents = discord.Intents.default()
intents.members = True
intents.typing = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", help_command=None,intents=intents)

# The message queue
class Msg:
    message: discord.Message
    reply: str

# global msgqueue
msgqueue=[]
# store all channels    
channels=[]

# Thread to answer all queries in the msgqueue
def thread_generate():
    while(True):
        time.sleep(1)
        if len(msgqueue)>0:
            msg=msgqueue[0]
            try:
                if (len(msg.reply)==0):
                    msg.reply=answerMessage(msg.message)
            except Exception as e:
                    msg.reply=("Error in reply: " + str(e))
                    print(msg)
                    pass

# This is the discord reply thread
@tasks.loop(seconds=1)
async def thread_reply():
        global msgqueue
        if len(msgqueue)>0:
            reply=msgqueue[0].reply
            message=msgqueue[0].message
            # write 'typing' in every channel
            if message.channel not in channels:
                channels.append(message.channel)
            for channel in channels:
                await channel.typing()
            try:
                if (len(reply)>0):
                    print (f'reply received: {reply}')
                    msg=msgqueue.pop(0)
                    await bot.change_presence(activity=discord.Game(name='Queue: %d'% len(msgqueue)))
                    #send reply
                    if len(reply)>1500:
                        for i in range(0,len(reply),1500):
                            await message.channel.send(reply[i:i+1500], reference=message)
                    else:
                        await message.channel.send(reply,reference=message)
            except Exception as e:
                print("Error sending reply: " + str(e))
                pass

# Discord commands
@bot.command()
async def info(ctx):
    await ctx.send(ctx.guild)
    await ctx.send(ctx.author)

# Write the 'waking up' message
@bot.event
async def on_ready() -> None:
    msg=f"Bot {bot.user} waking up."
    print(msg)
    log(msg)
    await bot.change_presence(activity=discord.Game(name="")) 
    thread_reply.start()

# Enqueue all new messages directed to the bot
@bot.event
async def on_message(message):
    global msgqueue
    if message.author == bot.user:
        return
    botid=("<@%d>" % bot.user.id)
    print ('message received: %s %s' % (botid,message.content))
    if message.content.startswith(botid):
        print ('message accepted.')
        newMsg = Msg()
        newMsg.message=message
        newMsg.reply=""
        msgqueue.append(newMsg)
        

def answerMessage(message):
    #default parameters
    temperature= 0.72
    top_p= 0.5
    top_k=40
    repetition_penalty=1.2
    max_len=1500
    seed=1

    # Define the server address and port
    service_name = 'Guanaco-65b'
    hub=neuroengine(service_name=service_name)

    #We remove user names
    query = re.sub(r'<.*?>', '', message.content).strip()
    
    # Allow in-message change of parameters via json
    jsonStart=query.find('{')
    jsonEnd=query.find('}')
    if (jsonStart==0):
        try:
                if (jsonEnd>0): # json config present, parse
                    config=query[:jsonEnd+1]
                    query=query[jsonEnd+1:].strip()
                    config=json.loads(config)
                    if not (config.get('temperature') is None):
                        temperature=float(config['temperature'])
                    if not (config.get('top_p') is None):
                        top_p=float(config['top_p'])
                    if not (config.get('top_k') is None):
                        top_k=int(config['top_k'])
                    if not (config.get('seed') is None):
                        seed=int(config['seed'])
                    if not (config.get('max_len') is None):
                        max_len=int(config['max_len'])
                        if (max_len>2048): max_len=2048
        except Exception as e:
                msg = f"{message.author.mention} Error parsing the Json config: %s" % str(e)
                print(msg)
                return(msg)

    #Make the request
    response=hub.request(prompt=query,temperature=temperature,top_p=top_p,top_k=top_k,repetition_penalty=repetition_penalty,seed=seed,max_new_len=max_len)
    return response

def main():
    # Starting reply thread
    print('Starting reply thread')
    x = threading.Thread(target=thread_generate,args=())
    x.start()
    # Connect bot
    token=open('discordtoken.txt').read().strip()
    bot.run(token)

main()
