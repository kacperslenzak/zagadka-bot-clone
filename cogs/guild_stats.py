from discord.ext import commands, tasks
from discord import Status, Object
from discord.utils import get
from settings import server_stats_channel

class GuildStats(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.members_channel = server_stats_channel['total_members']
        self.online_channel = server_stats_channel['total_online']
        self.voice_channel = server_stats_channel['total_in_voice']
        self.refresh_stats.start()

    def cog_unload(self):
        self.refresh_stats.cancel()

    @tasks.loop(hours=1)
    async def refresh_stats(self):
        guild = self.client.get_guild(self.client.guild_id)
        members = len(guild.members)
        online_members = len([member for member in guild.members if member.status is Status.online or member.status is Status.dnd])
        voice_members = len([member for member in guild.members if member.voice])

        members_channel = get(guild.channels, id=self.members_channel)
        online_channel = get(guild.channels, id=self.online_channel)
        voice_channel = get(guild.channels, id=self.voice_channel)
        await members_channel.edit(name=f"Members: {members}")
        await online_channel.edit(name=f"Online: {online_members}")
        await voice_channel.edit(name=f"Voice: {voice_members}")


def setup(client):
    client.add_cog(GuildStats(client))