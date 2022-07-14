from discord.ext import commands
from discord.utils import get
from discord import Object


class MutedRoleManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = self.client.get_guild(self.client.guild_id)
        text_muted_role = get(guild.roles, name='⌀')
        image_muted_role = get(guild.roles, name='☢︎')
        red_color_role = get(guild.roles, name='🔴')
        green_color_role = get(guild.roles, name='🟢')
        blue_color_role = get(guild.roles, name='🔵')
        mute_roles = (text_muted_role, image_muted_role)

        color_roles = (red_color_role, green_color_role, blue_color_role)

        if (text_muted_role not in before.roles or image_muted_role not in before.roles) and (text_muted_role in after.roles or image_muted_role in after.roles):
            roles = [Object(r.id) for r in after.roles if r not in color_roles or r not in mute_roles]
            return await before.edit(roles=roles)


def setup(client):
    client.add_cog(MutedRoleManager(client))
