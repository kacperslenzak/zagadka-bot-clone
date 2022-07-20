from discord import PermissionOverwrite, HTTPException, Forbidden, NotFound
from discord.ext import commands
from settings import authorized_create_channel_id


class ChannelManager(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is None:
            return

        if (before.channel is None and after.channel is not None) or (before.channel is not None and before.channel is not after.channel):
            if after.channel and after.channel.id in authorized_create_channel_id:
                if after.channel.category.name.__contains__('max_'):
                    limit = after.channel.category.name.split('_')[1]
                else:
                    limit = 0
                perms = {'speak': True, 'connect': True, 'priority_speaker': True}
                created_vc = await after.channel.category.create_voice_channel(
                    name=f"-{member.display_name}",
                    reason=f"Creating channel for {member}",
                    overwrites=None,
                    bitrate=64527,
                    user_limit=int(limit)
                )

                await created_vc.set_permissions(member, overwrite=PermissionOverwrite(**perms))

                try:
                    await member.move_to(created_vc)
                except (Forbidden, HTTPException):
                    await created_vc.delete(reason="channel deleted: forbidden")
                except NotFound:
                    pass
                else:
                    if member.voice is None:
                        await created_vc.delete(reason="channel deleted: no member")

        if before.channel is not None and (after.channel is None or after.channel is not None):
            if len(before.channel.members) <= 0:
                if before.channel.bitrate == 64527:
                    try:
                        await before.channel.delete(reason="Channel was deleted because it was marked as a temp channel [bitrate ~ 64.5k]")
                    except (Forbidden, NotFound, HTTPException):
                        pass


def setup(client):
    client.add_cog(ChannelManager(client))
