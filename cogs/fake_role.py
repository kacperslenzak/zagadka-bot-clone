from discord.ext import commands, tasks
from discord.utils import get


class FakeRole(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = list()
        self.remove_fake_roles.start()

    def cog_unload(self):
        self.remove_fake_roles.cancel()

    @tasks.loop(minutes=10)
    async def remove_fake_roles(self):
        guild = self.client.get_guild(self.client.guild_id)
        everyone_role, here_role = get(guild.roles, name='everyone'), get(guild.roles, name='here')
        if self.queue:
            member = get(guild.members, id=self.queue[-1])
            if everyone_role in member.roles and here_role in member.roles:
                await member.remove_roles(everyone_role, here_role)
            else:
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        everyone_role = get(message.guild.roles, name='everyone')
        here_role = get(message.guild.roles, name='here')
        if f"<@&{everyone_role.id}>" in message.content or f"<@&{here_role.id}>" in message.content:
            if message.author.id in self.queue:
                self.queue.remove(message.author.id)
                self.queue.append(message.author.id)
            else:
                await message.author.add_roles(everyone_role, here_role)
                self.queue.append(message.author.id)


def setup(client):
    client.add_cog(FakeRole(client))
