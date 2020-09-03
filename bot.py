import discord
from discord.ext import commands
from asyncio import sleep
from datetime import datetime
from datetime import timedelta
from datetime import time

client = commands.Bot(command_prefix='!')
memberDBDict = {}
memberCreated = []


def readToken():
    with open("token.txt", "r") as input:
        lines = input.readlines()
        return lines[0].strip()


token = readToken()

async def getMembers():
    while True:
        #print("Getting Members")
        for member in client.get_all_members():
            memberName = member.name
            roleFound = False
            if member.activity is None:
                memberDict = {"member": member, "notif30": 1, "notif60": 1, "notif90": 1, "notifOnce": 0,
                              "lastnotif": datetime.utcnow(), 'lastAct': None, "actStart": datetime.utcnow()}
            elif int(member.activity.type) == 0:
                memberDict = {"member": member, "notif30": 1, "notif60": 1, "notif90": 1, "notifOnce": 0,
                            "lastnotif": datetime.utcnow(), 'lastAct': member.activity.name, "actStart": member.activity.created_at}
            else:
                memberDict = {"member": member, "notif30": 1, "notif60": 1, "notif90": 1, "notifOnce": 0,
                              "lastnotif": datetime.utcnow(), 'lastAct': member.activity.name,
                              "actStart": datetime.utcnow()}
            for role in member.roles:
                if role.name == "GameTime Users":
                    roleFound = True
                if role.name == "GT 60 Min":
                    memberDict["notif30"] = 0
                if role.name == "GT 90 Min":
                    memberDict["notif30"] = 0
                    memberDict["notif60"] = 0
            if roleFound and memberName not in memberCreated:
                print(f"Member Added/Overwritten: {memberName}")
                memberDBDict[memberName] = memberDict
                memberCreated.append(memberName)
            elif roleFound is False and memberName in memberCreated:
                print(f"Member Removed: {memberName}")
                memberDBDict.pop(memberName)
                memberCreated.clear(memberName)
        await sleep(5)


async def sendDM(member, gamingtime):
    timeParse = (datetime.min + gamingtime).time()
    if timeParse.hour == 0:
        message = f"Consider taking a break. You have been playing for {timeParse.minute} minutes!"
    elif timeParse.hour == 1 and timeParse.minute == 0:
        message = f"Consider taking a break. You have been playing for 1 hour!"
    elif timeParse.hour == 1 and timeParse.minute != 0:
        message = f"Consider taking a break. You have been playing for 1 hour and {timeParse.minute} minutes!"
    elif timeParse.hour > 1 and timeParse.minute == 0:
        message = f"Consider taking a break. You have been playing for {timeParse.hour} hours!"
    elif timeParse.hour > 1 and timeParse.minute != 0:
        message = f"Consider taking a break. You have been playing for {timeParse.hour} hours"
        message += f" and {timeParse.minute} minutes!"
    await member.send(content=message, delete_after=10)
    print(f"Message sent to {member}: {message}")


async def deployNotifs():
    while True:
        #print("Sending Notifications if any.")
        for memberName in memberDBDict:
            #print(memberDBDict[memberName]["member"])
            if memberDBDict[memberName]["member"].activity is not None:
                if memberDBDict[memberName]["member"].activity.name == memberDBDict[memberName]["lastAct"]:
                    if int(memberDBDict[memberName]["member"].activity.type) == 0:
                        timeGaming = datetime.utcnow() - memberDBDict[memberName]["actStart"]
                        timeLimit30 = timedelta(minutes=30)
                        timeLimit60 = timedelta(minutes=60)
                        timeLimit90 = timedelta(minutes=90)
                        timeLimit120 = timedelta(minutes=120)
                        timeSinceNotif = datetime.utcnow() - memberDBDict[memberName]["lastnotif"]
                        notifLimit = timedelta(minutes=30)
                        #print(f"{memberDBDict[memberName]['member'].name}: {memberDBDict[memberName]['member'].activity.name}: {str(timeGaming)}")
                        if memberDBDict[memberName]["notifOnce"] == 0:
                            #print("This was triggered!")
                            timeSinceNotif = notifLimit
                            memberDBDict[memberName]["notifOnce"] = 1
                        if timeGaming >= timeLimit120:
                            if timeSinceNotif >= notifLimit:
                                memberDBDict[memberName]["lastnotif"] = datetime.utcnow()
                                await sendDM(memberDBDict[memberName]["member"], timeGaming)
                        elif timeGaming >= timeLimit90 and memberDBDict[memberName]["notif90"] == 1:
                            if timeSinceNotif >= notifLimit:
                                memberDBDict[memberName]["lastnotif"] = datetime.utcnow()
                                await sendDM(memberDBDict[memberName]["member"], timeGaming)
                        elif timeGaming >= timeLimit60 and memberDBDict[memberName]["notif60"] == 1:
                            if timeSinceNotif >= notifLimit:
                                memberDBDict[memberName]["lastnotif"] = datetime.utcnow()
                                await sendDM(memberDBDict[memberName]["member"], timeGaming)
                        elif timeGaming >= timeLimit30 and memberDBDict[memberName]["notif30"] == 1:
                            #print(timeSinceNotif)
                            if timeSinceNotif >= notifLimit:
                                memberDBDict[memberName]["lastnotif"] = datetime.utcnow()
                                await sendDM(memberDBDict[memberName]["member"], timeGaming)
                else:
                    #print("Changing Activity")
                    memberDBDict[memberName]["lastAct"] = memberDBDict[memberName]["member"].activity.name
                    memberDBDict[memberName]["actStart"] = memberDBDict[memberName]["member"].activity.created_at
            else:
                #print("Changing to None")
                memberDBDict[memberName]["lastAct"] = memberDBDict[memberName]["member"].activity
                memberDBDict[memberName]["actStart"] = datetime.utcnow()
        await sleep(10)

@client.event
async def on_raw_reaction_add(payload):
    # Set GameTime User Role
    member = payload.member
    #print(f"{member.name} reacted")
    channel = discord.utils.get(client.get_all_channels(), id=727621686085812236)
    if payload.message_id == 727768829387604019:
        role = discord.utils.get(member.guild.roles, name="GameTime Users")
        #print(f"Adding {role} role to {member}")
        await member.add_roles(role, reason="GameTime enabled!")
    if payload.message_id == 727768830658478120:
        if payload.emoji.id == 727664758731309168:
            role = discord.utils.get(member.guild.roles, name="GT 60 Min")
            # print(f"Adding {role} role to {member}")
            await member.add_roles(role, reason="GT 60 Min Enabled!")
    if payload.message_id == 727768830658478120:
        if payload.emoji.id == 727664758853074995:
            role = discord.utils.get(member.guild.roles, name="GT 90 Min")
            # print(f"Adding {role} role to {member}")
            await member.add_roles(role, reason="GT 90 Min Enabled!")


@client.event
async def on_raw_reaction_remove(payload):
    member = discord.utils.get(client.get_all_members(), id=payload.user_id)
    #print(f"{member.name} unreacted")
    if payload.message_id == 727768829387604019:
        role = discord.utils.get(member.guild.roles, name="GameTime Users")
        #print(f"Adding {role} role to {member}")
        await member.remove_roles(role, reason="GameTime enabled!")
    if payload.message_id == 727768830658478120:
        if payload.emoji.id == 727664758731309168:
            role = discord.utils.get(member.guild.roles, name="GT 60 Min")
            # print(f"Adding {role} role to {member}")
            await member.remove_roles(role, reason="GT 60 Min Enabled!")
    if payload.message_id == 727768830658478120:
        if payload.emoji.id == 727664758853074995:
            role = discord.utils.get(member.guild.roles, name="GT 90 Min")
            # print(f"Adding {role} role to {member}")
            await member.remove_roles(role, reason="GT 90 Min Enabled!")


@client.event
async def on_member_join(member):
    welchannel = discord.utils.get(client.get_all_channels(), id=727621335345397911)
    howtochannel = discord.utils.get(client.get_all_channels(), id=727621686085812236)
    message = f"Welcome {member.mention}!\nPlease follow the instructions in {howtochannel.mention} to get GameTime up and running!\n_ _\n"
    await welchannel.send(content=message)

@client.event
async def on_ready():
    print("GameTime is online!")
    client.loop.create_task(getMembers())
    client.loop.create_task(deployNotifs())


client.run(token)