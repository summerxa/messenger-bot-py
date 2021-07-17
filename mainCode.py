# bot.py
import os
import asyncio
import json
import time

import discord
from dotenv import load_dotenv

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

prefixes = ["m!", "M!"]

bot = commands.Bot(command_prefix=prefixes)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

servInfo = {}
with open("C:\\Users\\MangoPotato\\projects\\MessageBotPy\\server_info.json", "r") as read_file:
    servInfo = json.load(read_file)

servMail = servInfo["mail"]
servNotf = servInfo["notifs"]

def j_dump():
    with open("C:\\Users\\MangoPotato\\projects\\MessageBotPy\\server_info.json", "w") as write_file:
        json.dump(servInfo, write_file)

def in_server(s_id):
    low = 0
    high = len(bot.guilds) - 1
    while low <= high:
        mid = (low + high)//2
        if bot.guilds[mid].id == s_id:
            return True
        elif bot.guilds[mid].id < s_id:
            low = mid + 1
        elif bot.guilds[mid].id > s_id:
            high = mid - 1
    return False

def display_notif(g_id, ind):
    em = discord.Embed(title="You've received a message!",description="#" + str(ind+1) + " for this server")
    title = "From "
    body = servMail[g_id][ind][2]
    if len(body) > 50:
        body = body[:49] + "..."
    elif len(body) == 0:
        body = "[MESSAGE CONTAINS NO TEXT]"
    try:
        server = bot.get_guild(servMail[g_id][ind][0])
        title += server.name
    except:
        title = "[SERVER IS UNAVAILABLE]"
    em.add_field(name=title, value=body, inline=False)
    return em

@bot.command(name='send', help='Send a message to another server. ',
             usage='[OPTIONAL destination server ID]')
async def server_send(ctx, *args):
    msg = ctx
    files = []

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    await ctx.send("Respond with a message in 60 seconds.")
    try:
        msg = await bot.wait_for('message', timeout=60.0, check=check)
        for file in msg.attachments:
            files.append(file.url)
    except asyncio.TimeoutError:
        await ctx.send("Request timed out.")
        return
    
    loop = False
    s_id = 0
    if len(args) > 0:
        try:
            s_id = int(args[0])
            loop = not in_server(s_id)
        except:
            loop = True
    else:
        loop = True
    if loop:
        await ctx.send("What is the ID of the server you are sending this message to?\n"
                        "**Note:** bot must be in server for this to work.")
        while (True):
            try:
                s_id = await bot.wait_for('message', timeout=30.0, check=check)
                try:
                    s_id = int(s_id.content)
                    if in_server(s_id):
                        break
                except ValueError:
                    continue
            except asyncio.TimeoutError:
                await ctx.send("Request timed out.")
                return
            await ctx.send("Bot is not in this server. Try again:")
    
    s_id = str(s_id)
    if s_id in servMail:
        servMail[s_id].append([msg.guild.id, msg.author.id, msg.content])
    else:
        servMail[s_id] = [[msg.guild.id, msg.author.id, msg.content]]
    if len(files) > 0:
        for i in files:
            servMail[s_id][len(servMail[s_id]) - 1].append(i)
    async with ctx.typing():
        if s_id in servNotf:
            c_id = servNotf[s_id]
            if c_id < 0:
                return
            try:
                chnl = await bot.fetch_channel(c_id)
                await chnl.send(embed=display_notif(s_id, len(servMail[s_id]) - 1))
            except:
                servNotf[s_id] = -1
        j_dump()
    await ctx.send("Message saved successfully.")

def display_page(g_id, curPage):
    L = len(servMail[g_id])
    pages = L//5 + min(1, L%5)
    em = discord.Embed(title="",description="Showing page " + str(curPage+1) + " of " + str(max(pages,1)))
    for i in range(curPage * 5, min(L, curPage * 5 + 5)):
        title = str(i + 1) + ". "
        body = servMail[g_id][i][2]
        if len(body) > 50:
            body = body[:49] + "..."
        elif len(body) == 0:
            body = "[MESSAGE CONTAINS NO TEXT]"
        try:
            server = bot.get_guild(servMail[g_id][i][0])
            title += server.name
        except:
            title += "[SERVER IS UNAVAILABLE]"
        em.add_field(name=title, value=body, inline=False)
    return em

@bot.command(name='mail', help='View the messages in your current server\'s mailbox.')
async def serv_mail(ctx):
    curPage = 0
    g_id = str(ctx.message.guild.id)

    if not g_id in servMail:
        await ctx.channel.send("Your server has not received mail yet!")
        return
    
    em = display_page(g_id, curPage)
    display = await ctx.channel.send(embed=em)
    await display.add_reaction('\U00002b05') # left
    await display.add_reaction('\U000027a1') # right

    def check(reaction, user):
        return reaction.message == display and user == ctx.message.author
    
    timeout = time.time() + 60
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            if reaction.emoji == '\U00002b05':
                curPage = max(0, curPage - 1)
                em = display_page(g_id, curPage)
            elif reaction.emoji == '\U000027a1':
                curPage = min(len(servMail[g_id])//5 + min(1,len(servMail[g_id]) % 5) - 1, curPage+1)
                em = display_page(g_id, curPage)
            await display.edit(embed=em)
        except asyncio.TimeoutError:
            break
        if time.time() > timeout:
            break

@bot.command(name='view', help='View a specific message.', usage='[index of message]')
async def view_serv_mail(ctx, *args):
    ind = 0
    mail = [0, 0, 0]
    if len(args) == 0:
        await ctx.channel.send("Message index is missing.\n"
            "Command should be used as: `m!view [index]`")
        return
    else:
        try:
            ind = int(args[0]) - 1
            mail = servMail[str(ctx.message.guild.id)][ind]
        except:
            if not str(ctx.message.guild.id) in servMail:
                await ctx.channel.send("Your server has not received mail yet!")
                return
            elif ind < 0 or ind >= len(servMail[str(ctx.message.guild.id)]):
                await ctx.channel.send("Index is invalid.")
                return
    title = "Message #" + str(ind + 1)
    auth = "Sent from "
    aurl = ""
    try:
        server = bot.get_guild(mail[0])
        auth += server.name
        aurl = str(server.icon_url)
    except:
        auth = "[SERVER IS UNAVAILABLE]"
    em = discord.Embed(title=title,description=mail[2])
    em.set_author(name=auth, icon_url=aurl)
    foot = "Message written by "
    furl = ""
    try:
        user = await bot.fetch_user(mail[1])
        foot += user.name + "#" + user.discriminator
        furl = str(user.avatar_url)
    except:
        foot = "[USER IS UNAVAILABLE]"
    em.set_footer(text=foot, icon_url=furl)
    if len(mail) > 3:
        filestr = ""
        for i in range(3, len(mail)):
            filestr += mail[i]
            if i < len(mail) - 1:
                filestr += '\n'
        em.add_field(name="Attached Files:", value=filestr)
    await ctx.channel.send(embed=em)

@bot.command(name='delete', help='Delete a specific message.', usage='[index of message]')
async def delete_serv_mail(ctx, *args):
    ind = 0
    g_id = str(ctx.message.guild.id)
    if len(args) == 0:
        await ctx.channel.send("Message index is missing.\n"
            "Command should be used as: `m!delete [index]`")
        return
    else:
        try:
            ind = int(args[0]) - 1
        except:
            await ctx.channel.send("Index is invalid.")
            return
    if not g_id in servMail:
        await ctx.channel.send("Your server has not received mail yet!")
        return
    elif ind < 0 or ind >= len(servMail[g_id]):
        await ctx.channel.send("Index is invalid.")
        return
    
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    
    await ctx.channel.send("Are you sure you want to delete this message?\n"
                           "Respond with **y**es/**n**o within 30 seconds.")
    while (True):
        try:
            response = await bot.wait_for('message', timeout=30.0, check=check)
            response = response.content.lower()
            if response[0] == 'y':
                break
            elif response[0] == 'n':
                await ctx.channel.send("Action has been cancelled.")
                return
        except asyncio.TimeoutError:
            await ctx.send("Request timed out.")
            return
        await ctx.send("That's not a valid response. Try again:")
    del servMail[g_id][ind]
    if len(servMail[g_id]) == 0:
        del servMail[g_id]
    async with ctx.typing():
        j_dump()
    await ctx.send("Message deleted successfully.")

@bot.command(name='notifs', help='Send a notification when you receive a message. '
                'Using the command toggles notifications on/off in the current channel. ',
                 usage='[true/false]')
async def toggle_notifs(ctx, *true_false):
    chnl = ctx.channel.id
    if len(true_false) == 0:
        await ctx.channel.send("On/off is missing."
            "Command should be used as: `m!notifs [true/false]`")
    true_false = true_false[0].lower()
    response = ""
    if true_false[0] == 't':
        servNotf[str(ctx.message.guild.id)] = chnl
        response = "Notifications set to this channel.\n**NOTE:** Bot will only send notifications in the most recent channel."
    elif true_false[0] == 'f':
        servNotf[str(ctx.message.guild.id)] = -1
        response = "Notifications turned off in this channel."
    else:
        await ctx.channel.send("Command should be used as: `m!notifs [true/false]`")
        return
    async with ctx.typing():
        j_dump()
    await ctx.channel.send(content=response)

def display_list(guilds, L, g_id, curPage):
    pages = L//5 + min(1, L%5)
    em = discord.Embed(title="",description="Showing page " + str(curPage+1) + " of " + str(max(pages,1)))
    
    body = ""
    for guild in guilds[curPage*5:min(L, curPage*5 + 5)]:
        body += guild.name
        if guild.id == g_id:
            body += ' (this server)'
        body += ' - ' + str(guild.id) + '\n'
    em.add_field(name="Servers are sorted by ID.", value=body, inline=False)
    return em

@bot.command(name='list', help='View all the servers you can send messages to (including their IDs).')
async def serv_list(ctx):
    guilds = bot.guilds
    L = len(guilds)
    nPages = (L//5 + min(1,L) % 5) - 1
    curPage = 0
    g_id = ctx.message.guild.id
    
    em = display_list(guilds, L, g_id, curPage)
    display = await ctx.channel.send(embed=em)
    await display.add_reaction('\U00002b05') # left
    await display.add_reaction('\U000027a1') # right

    def check(reaction, user):
        return reaction.message == display and user == ctx.message.author
    
    timeout = time.time() + 60
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            if reaction.emoji == '\U00002b05':
                curPage = max(0, curPage - 1)
                em = display_list(guilds, L, g_id, curPage)
            elif reaction.emoji == '\U000027a1':
                curPage = min(nPages, curPage+1)
                em = display_list(guilds, L, g_id, curPage)
            await display.edit(embed=em)
        except asyncio.TimeoutError:
            break
        if time.time() > timeout:
            break

bot.run(TOKEN)
