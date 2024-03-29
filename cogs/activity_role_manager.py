import traceback
import pymongo
import discord
from discord.ext import commands, tasks
from discord import Object
from discord.utils import get


class ActivityRoleManager(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.rangi = client.get_guild(self.client.guild_id).roles
        self.ranking_roles = dict()
        for x in range(1, 128):
            role = discord.utils.get(self.rangi, name=str(x))
            self.ranking_roles[int(x)] = role.id
        self.role_ids = list(self.ranking_roles.values())
        self.assign_roles.start()

    def cog_unload(self):
        self.assign_roles.cancel()

    @tasks.loop(hours=1)
    async def assign_roles(self):
        ranking = [int(user['_id']) async for user in
                   self.client.db.users.find({}, {"_id": True}).limit(128).sort('points', pymongo.DESCENDING) if type(user['_id']) is str]

        guild = self.client.get_guild(self.client.guild_id)

        async def assign_roles(user, roles_param):
            try:
                await user.edit(roles=roles_param)
            except Exception:
                traceback.print_exc()
                pass

        async def remove_members_from_role(role):
            try:
                for member in role.members:
                    await member.remove_roles(role)
            except Exception:
                traceback.print_exc()
                pass

        queue = []
        for i, user_id in enumerate(ranking):
            user = guild.get_member(user_id)

            if (not user) or user.bot:
                continue

            if self.ranking_roles.get(i+1, 128) in [r.id for r in user.roles]:
                continue

            roles = [Object(r.id) for r in user.roles if r.id not in self.role_ids]
            role = get(guild.roles, id=self.ranking_roles.get(i+1, 128))
            roles.append(role)

            if len(role.members) > 1 and user not in role.members:
                queue.append(self.client.loop.create_task(remove_members_from_role(role)))

            queue.append(self.client.loop.create_task(assign_roles(user, roles)))

            for action in queue:
                await action


def setup(client):
    client.add_cog(ActivityRoleManager(client))
