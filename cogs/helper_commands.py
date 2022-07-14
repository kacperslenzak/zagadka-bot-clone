import asyncio
import ast
from discord.ext import commands
from discord.utils import get
import discord
import pymongo

def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class HelperCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='echo')
    @commands.has_guild_permissions(administrator=True)
    async def echo(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name='mutelive')
    @commands.has_guild_permissions(administrator=True)
    async def mutelive(self, ctx, user: discord.Member = None):
        if not user:
            return
        mutelive_role = get(ctx.guild.roles, name='⚠︎')

        if mutelive_role in user.roles:
            return

        await user.add_roles(mutelive_role)

    @commands.command(name='unmutelive')
    @commands.has_guild_permissions(administrator=True)
    async def unmutelive(self, ctx, user: discord.Member = None):
        if not user:
            return
        mutelive_role = get(ctx.guild.roles, name='⚠︎')

        if mutelive_role not in user.roles:
            return

        await user.remove_roles(mutelive_role)

    @commands.command(name='clean')
    @commands.has_guild_permissions(administrator=True)
    async def clean(self, ctx, user: discord.Member = None):
        if not user:
            return

        asyncio.ensure_future(
            ctx.channel.purge(limit=200, check=lambda msg: msg.author == user)
        )

    @commands.command(name='eval')
    @commands.is_owner()
    async def eval(self, ctx, *, cmd):
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = (await eval(f"{fn_name}()", env))
        await ctx.send(result)

    @commands.command(name='avatar', aliases=['a'])
    async def avatar(self, ctx, user: discord.Member = None):
        user = user if user else ctx.author
        return await ctx.send(user.avatar_url)

    @commands.command(name='top', aliases=['t', 'tm'])
    async def top(self, ctx):
        topka = str()
        async for user in self.client.db.users.find({}).limit(10).sort('points', pymongo.DESCENDING):
            member = get(ctx.guild.members, id=int(user['_id']))
            topka += f"{member.name}: {user['points']} \n"

        em = discord.Embed(color=discord.Colour.from_rgb(0, 0, 0,), title="Topka", description=f"```{topka}```")
        await ctx.send(embed=em)

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def sync_users(self, ctx):
        async for user in self.client.db.users.find({}):
            if type(user['_id']) == str():
                member = get(ctx.guild.members, id=int(user['_id']))
                if not member:
                    self.client.db.users.delete_one({'_id': user['_id']})

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def resetpoints(self, ctx, user: discord.Member):
        if not user:
            return
        user = await self.client.db.users.find_one({'_id': str(user.id)})
        if user:
            await self.client.db.users.update_one(
                {"_id": user['_id']}, {"$set": {"points": 0}}
            )

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def everyone(self, ctx):
        await ctx.message.delete()
        allowed_mentions = discord.AllowedMentions(everyone=True)
        return await ctx.send(content="@everyone", allowed_mentions=allowed_mentions)


def setup(client):
    client.add_cog(HelperCommands(client))
