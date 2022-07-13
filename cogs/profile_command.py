import discord
from discord.ext import commands
from typing import Optional
from zagadkabot.invite_utils import fetch_user_invites


class ProfileCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="profile", aliases=['p'])
    async def profile(self, ctx, user: Optional[discord.Member]):
        user: discord.Member = user or ctx.author
        invites = await fetch_user_invites(self, user)

        em = discord.Embed()
        em.set_author(name=user.name, icon_url=user.avatar_url)
        em.add_field(name="created at", value=user.created_at.strftime("%d/%m/%y\n%H:%M:%S"), inline=True)
        em.add_field(name="joined at", value=user.joined_at.strftime("%d/%m/%y\n%H:%M:%S"), inline=True)
        if len(user.roles) > 1:
            em.add_field(name="roles", value=f"".join(f'{r.name}, ' for r in user.roles if r.name != "@everyone"), inline=True)
        em.add_field(name="invited people", value=f"{invites[0]}({sum([invites[0], invites[1], invites[2]])})", inline=False)
        em.set_footer(text="invited by zagadka")

        await ctx.send(embed=em)


def setup(client):
    client.add_cog(ProfileCommand(client))