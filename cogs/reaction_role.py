from discord.ext import commands
import discord
from discord.utils import get
from settings import reaction_role_channel_id


class ReactionRole(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.get_guild(self.client.guild_id)
        red_role = get(guild.roles, name='🔴')
        green_role = get(guild.roles, name='🟢')
        blue_role = get(guild.roles, name='🔵')
        roles = [red_role, green_role, blue_role]
        if payload.channel_id == reaction_role_channel_id:
            current_role = [r for r in payload.member.roles if r in roles]
            if current_role:
                await payload.member.remove_roles(current_role[0])
                await payload.member.add_roles(get(guild.roles, name=payload.emoji.name))
            else:
                await payload.member.add_roles(get(guild.roles, name=payload.emoji.name))

            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.remove_reaction(payload.emoji, payload.member)


def setup(client):
    client.add_cog(ReactionRole(client))