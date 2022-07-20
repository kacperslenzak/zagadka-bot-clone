import discord
from discord.ext import commands
from typing import Optional

import datetime

class ReputationManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_if_rep_field_exists(self, ctx, user):
        user_query = await self.client.db.users.find_one({'_id': str(user.id), 'reputation': {'$exists': True}})
        if not user_query:
            await self.client.db.users.update_one({"_id": str(user.id)}, {"$set": {"reputation": 0}},
                                                  upsert=True)

        user_query = await self.client.db.users.find_one({'_id': str(user.id)})

        return user_query

    @commands.group(invoke_without_command=True)
    async def r(self, ctx, user: Optional[discord.Member]):
        user = ctx.author if user is None else user
        user_query = await self.check_if_rep_field_exists(ctx, user)
        command = self.client.get_command("r add")
        cooldown_message = "mozesz juz przydzielic" if command.get_cooldown_retry_after(ctx) == 0.0 else f"mozesz przydzielic za {datetime.timedelta(seconds=round(command.get_cooldown_retry_after(ctx)))}"
        if user_query and user == ctx.author:
            await ctx.reply(f"Stan twojej reputacji: **{user_query['reputation']}**, {cooldown_message}")
        elif user_query:
            await ctx.reply(f"Stan reputacji {user.name}: **{user_query['reputation']}**")

    @r.group(aliases=['+'])
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def add(self, ctx, user: Optional[discord.Member]):
        user_query = await self.check_if_rep_field_exists(ctx, user)
        if not user or user == ctx.author:
            await ctx.send("Nie mozesz dodac sobie reputacji!")
        elif user and user is not ctx.author:
            await self.client.db.users.update_one({"_id": str(user.id)}, {"$inc": {"reputation": 1}}, upsert=True)
            user_query = await self.client.db.users.find_one({'_id': str(user.id)})
            await ctx.reply(f"+1 punkt reputacji dla {user.name} razem: **{user_query['reputation']}**")

    @r.group(aliases=['-'])
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def remove(self, ctx, user: Optional[discord.Member]):
        user_query = await self.check_if_rep_field_exists(ctx, user)
        if not user or user == ctx.author:
            await ctx.send("Nie mozesz dodac sobie reputacji!")
        elif user and user is not ctx.author:
            await self.client.db.users.update_one({"_id": str(user.id)}, {"$inc": {"reputation": -1}}, upsert=True)
            user_query = await self.client.db.users.find_one({'_id': str(user.id)})
            await ctx.reply(f"-1 punkt reputacji dla {user.name} razem: **{user_query['reputation']}**")


def setup(client):
    client.add_cog(ReputationManager(client))