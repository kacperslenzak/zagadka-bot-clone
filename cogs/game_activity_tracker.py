from discord import Member, ActivityType, Object
from discord.ext import commands, tasks
from discord.utils import get
from settings import game_roles


class GameActivityTracker(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.game_roles = {
            "Among Us": game_roles['Among Us'],
            "Apex Legends": game_roles['Apex Legends'],
            "Call Of Duty": game_roles['Call Of Duty'],
            "Counter Strike": game_roles['Counter Strike'],
            "Dead By Daylight": game_roles['Dead By Daylight'],
            "Fortnite": game_roles['Fortnite'],
            "Grand Theft Auto V": game_roles['Grand Theft Auto V'],
            "League Of Legends": game_roles['League Of Legends'],
            "Minecraft": game_roles['Minecraft'],
            "Rainbow Six Siege": game_roles['Rainbow Six Siege'],
            "Rust": game_roles['Rust'],
            "ROBLOX": game_roles['ROBLOX'],
            "Rocket League": game_roles['Rocket League'],
            "VALORANT": game_roles['VALORANT'],
            "World of Tanks": game_roles['World Of Tanks']
        }
        self.games = self.game_roles.values()
        self.game_names = self.game_roles.keys()
        self.check_game_status.start()

    def cog_unload(self):
        self.check_game_status.cancel()

    @tasks.loop(minutes=1)
    async def check_game_status(self):
        guild = self.client.get_guild(self.client.guild_id)
        for member in guild.members:
            member: Member
            member_game_roles = [r for r in member.roles if r.id in self.games]
            if len(member_game_roles) > 0 and len(member.activities) == 0:
                await member.remove_roles(member_game_roles[0])
            elif member.activities:
                for activity in member.activities:
                    if len(member_game_roles) > 0:
                        if activity.name != member_game_roles[0].name:
                            await member.remove_roles(member_game_roles[0])
                    if activity.name in self.game_names:
                        await member.add_roles(Object(self.game_roles[activity.name]))



def setup(client):
    client.add_cog(GameActivityTracker(client))
