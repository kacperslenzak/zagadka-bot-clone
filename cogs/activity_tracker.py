import discord
from discord import Member
from discord.ext import commands, tasks
from discord.utils import get


class Points(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_punkty.start()

    def cog_unload(self):
        self.voice_punkty.cancel()

    @tasks.loop(minutes=1)
    async def voice_punkty(self):
        guild = self.client.get_guild(self.client.guild_id)
        for channel in guild.voice_channels:
            for user_id, state in channel.voice_states.items():
                if state.mute or state.deaf or state.self_mute or state.self_deaf or state.afk:
                    continue
                await self.client.db.users.update_one({"_id": str(user_id)}, {"$inc": {"points": int(20)}}, upsert=True)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not isinstance(msg.author, Member) or msg.author.bot:
            return

        slowa = [word for word in msg.content.strip().split(" ") if word.strip() != ""]
        points = 2 if len(slowa) >= 4 else 1

        voter_role = discord.utils.find(lambda r: r.name == '🟡', msg.guild.roles)
        booster_role = discord.utils.find(lambda r: r.name == "♼", msg.guild.roles)
        donator_1 = discord.utils.find(lambda r: r.name == "$1", msg.guild.roles)
        donator_2 = discord.utils.find(lambda r: r.name == "$2", msg.guild.roles)
        donator_4 = discord.utils.find(lambda r: r.name == "$4", msg.guild.roles)
        donator_8 = discord.utils.find(lambda r: r.name == "$8", msg.guild.roles)
        donator_16 = discord.utils.find(lambda r: r.name == "$16", msg.guild.roles)
        donator_32 = discord.utils.find(lambda r: r.name == "$32", msg.guild.roles)
        donator_64 = discord.utils.find(lambda r: r.name == "$64", msg.guild.roles)
        donator_128 = discord.utils.find(lambda r: r.name == "$128", msg.guild.roles)
        boost1_invite = discord.utils.find(lambda r: r.name == "⚃", msg.guild.roles)
        boost2_invite = discord.utils.find(lambda r: r.name == "⚂", msg.guild.roles)
        boost3_invite = discord.utils.find(lambda r: r.name == "⚁", msg.guild.roles)
        boost4_invite = discord.utils.find(lambda r: r.name == "⚀", msg.guild.roles)
        boost5_invite = discord.utils.find(lambda r: r.name == "♷", msg.guild.roles)
        boost6_invite = discord.utils.find(lambda r: r.name == "♶", msg.guild.roles)

        boosty = [1]

        if voter_role in msg.author.roles:
            boosty.append(0.10)

        if booster_role in msg.author.roles:
            boosty.append(0.25)

        if boost1_invite in msg.author.roles or \
                boost2_invite in msg.author.roles or \
                boost3_invite in msg.author.roles or \
                boost4_invite in msg.author.roles or \
                boost6_invite in msg.author.roles:
            boosty.append(0.25)

        elif boost5_invite in msg.author.roles:
            boosty.append(0.10)

        if donator_16 in msg.author.roles:
            boosty.append(0.60)

        elif donator_8 in msg.author.roles:
            boosty.append(0.30)

        elif donator_4 in msg.author.roles:
            boosty.append(0.20)

        elif donator_2 in msg.author.roles:
            boosty.append(0.10)

        elif donator_1 in msg.author.roles:
            boosty.append(0.05)

        if msg.author.activity:
            if msg.author.activity.name in ('dsc.gg/patelka', 'discord.gg/patelka', 'DISCORD.GG/PATELKA', '.gg/patelka', '.GG/PATELKA'):
                boosty.append(0.25)
                await msg.author.add_roles(get(msg.guild.roles, name='✦'))
            else:
                role = get(msg.guild.roles, name='✦')
                if role in msg.author.roles:
                    await msg.author.add_roles(get(msg.guild.roles, name='✦'))

        points *= sum(boosty)

        await self.client.db.users.update_one({"_id": str(msg.author.id)}, {"$inc": {"points": int(points)}}, upsert=True)


def setup(client):
    client.add_cog(Points(client))
