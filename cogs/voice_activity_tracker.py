from discord.ext import commands, tasks


class VoiceActivityTracker(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_activity_points.start()

    def cog_unload(self):
        self.voice_activity_points.cancel()

    @tasks.loop(minutes=1)
    async def voice_activity_points(self):
        guild = self.client.get_guild(self.client.guild_id)
        for channel in guild.voice_channels:
            for user_id, state in channel.voice_states.items():
                if state.mute or state.deaf or state.self_mute or state.self_deaf or state.afk:
                    continue
                await self.client.db.users.update_one({"_id": str(user_id)}, {"$inc": {"points": int(20)}}, upsert=True)


def setup(client):
    client.add_cog(VoiceActivityTracker(client))