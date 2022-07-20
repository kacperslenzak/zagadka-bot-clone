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
    @commands.has_guild_permissions(manage_messages=True)
    async def clean(self, ctx, user: discord.Member = None):
        if not user:
            return

        def check_message_author(msg):
            return msg.author == user or msg.author.name == user.name+"#"+user.discriminator

        asyncio.ensure_future(
            ctx.channel.purge(limit=200, check=check_message_author)
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

    @commands.command(name='toprep', aliases=['tr'])
    async def toprep(self, ctx):
        topka = str()
        async for user in self.client.db.users.find({}).limit(10).sort('reputation', pymongo.DESCENDING):
            member = get(ctx.guild.members, id=int(user['_id']))
            topka += f"{member.name}: {user['reputation']} \n"

        em = discord.Embed(color=discord.Colour.from_rgb(0, 0, 0,), title="Topka Repów", description=f"```{topka}```")
        await ctx.send(embed=em)

    @commands.command(name='toppoints', aliases=['tp'])
    async def toppoints(self, ctx):
        topka = str()
        async for user in self.client.db.users.find({}).limit(10).sort('points', pymongo.DESCENDING):
            print(user)
            member = get(ctx.guild.members, id=int(user['_id']))
            topka += f"{member.name}: {user['points']} \n"
        em = discord.Embed(color=discord.Colour.from_rgb(0, 0, 0, ), title="Topka Punktów", description=f"```{topka}```")
        await ctx.send(embed=em)

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def sync_users(self, ctx):
        async for user in self.client.db.users.find():
            if isinstance(user['_id'], str):
                member = ctx.guild.get_member(int(user['_id']))
                print(member)
                if member is None:
                    print(f'Usuwam: {user["_id"]}')
                    await self.client.db.users.delete_one({'_id': user['_id']})

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

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module: str):
        """Reloads a module."""
        try:
            self.client.unload_extension(module)
            self.client.load_extension(module)
        except Exception as e:
            await ctx.send('\N{PISTOL}')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{OK HAND SIGN}')


def setup(client):
    client.add_cog(HelperCommands(client))
