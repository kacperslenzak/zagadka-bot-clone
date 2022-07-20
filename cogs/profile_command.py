import discord
from discord.ext import commands
from typing import Optional
from zagadkabot.invite_utils import fetch_user_invites
from discord.utils import get

class ProfileCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="profile", aliases=['p'])
    async def profile(self, ctx, user: Optional[discord.Member]):
        user = user or ctx.author
        invites = await fetch_user_invites(self, user)
        user_db = await self.client.db.users.find_one({'_id': str(user.id)})

        em = discord.Embed()
        em.set_author(name=user.name, icon_url=user.avatar_url)
        em.add_field(name="created at", value=user.created_at.strftime("%d/%m/%y\n%H:%M:%S"), inline=True)
        em.add_field(name="joined at", value=user.joined_at.strftime("%d/%m/%y\n%H:%M:%S"), inline=True)
        if len(user.roles) > 1:
            em.add_field(name="roles", value=f"".join(f'{r.name} ' for r in user.roles if r.name != "@everyone"), inline=True)
        em.add_field(name="invited people", value=f"{invites[0]}({sum([invites[0], invites[1], invites[2]])})", inline=False)
        em.add_field(name="points", value=f"{user_db['points']}", inline=False)
        inviter = None
        if 'invited_by' in user_db:
            inviter = get(ctx.guild.members, id=int(user_db['invited_by']))
        em.set_footer(text=f"Invited by {inviter.name if inviter else 'PATELKA'}")

        await ctx.send(embed=em)


def setup(client):
    client.add_cog(ProfileCommand(client))