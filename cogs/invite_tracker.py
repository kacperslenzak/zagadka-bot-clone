import asyncio
import datetime
import time
from enum import IntEnum
from typing import Optional

import discord
from discord import Invite, Member, Embed, Colour
from discord.ext import commands
from discord.utils import get
from pymongo import UpdateOne
from zagadkabot.invite_utils import InviteType
from settings import member_join_logs_channel, member_leave_logs_channel

class Zaproszenia(commands.Cog):
    def __init__(self, client):
        self.client = client
        asyncio.create_task(self.sync())

    async def sync(self):
        for guild in self.client.guilds:
            invites = await guild.invites()
            await self.client.db.invites.bulk_write([
                UpdateOne({"_id": invite.code}, {"$set": {"uses": invite.uses}}, upsert=True)
                for invite in invites
            ])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        invites = await member.guild.invites()
        db_invites = {i['_id']: i for i in await self.client.db.invites.find(
            {"uses": {"$exists": True}}
        ).to_list(None)}

        await self.client.db.invites.bulk_write([
            UpdateOne({"_id": invite.code}, {"$set": {"uses": invite.uses}}, upsert=True)
            for invite in invites
        ])

        delta = datetime.timedelta(days=3) if member.avatar else datetime.timedelta(days=7)
        is_fake = member.created_at > datetime.datetime.today() - delta

        for invite in invites:
            invite: Invite

            if invite.code in db_invites and invite.uses != db_invites[invite.code]['uses']:
                channel = self.client.get_channel(member_join_logs_channel)
                inv = invite.inviter.id

                boost1_invite = discord.utils.find(lambda r: r.name == "♳", member.guild.roles)
                boost2_invite = discord.utils.find(lambda r: r.name == "♴", member.guild.roles)
                boost4_invite = discord.utils.find(lambda r: r.name == "♵", member.guild.roles)
                boost8_invite = discord.utils.find(lambda r: r.name == "♶", member.guild.roles)
                boost16_invite = discord.utils.find(lambda r: r.name == "♷", member.guild.roles)
                boost64_invite = discord.utils.find(lambda r: r.name == "♸", member.guild.roles)
                boost128_invite = discord.utils.find(lambda r: r.name == "♹", member.guild.roles)
                boost256_invite = discord.utils.find(lambda r: r.name == "⚀", member.guild.roles)
                boost512_invite = discord.utils.find(lambda r: r.name == "⚁", member.guild.roles)
                boost1024_invite = discord.utils.find(lambda r: r.name == "⚂", member.guild.roles)
                boost2048_invite = discord.utils.find(lambda r: r.name == "⚃", member.guild.roles)

                await self.client.db.users.update_one(
                    {"_id": str(member.id)}, {"$set": {
                        "invited_by": str(inv),
                        "invite_code": invite.code,
                        "invite_type": InviteType.FAKE.value if is_fake else InviteType.REGULAR.value,
                        "joined_at": int(member.joined_at.timestamp())
                    }}, upsert=True
                )

                await channel.send(
                    embed=Embed(
                        title=str(member),
                        color=Colour.green(),
                        description=f"Wszedł {member.mention} zaproszony przez <@{inv}> ({inv})"
                    ).set_thumbnail(url=str(member.avatar_url_as(format="png"))).set_footer(text=member.id)
                )

                regular = 0

                async for invite in self.client.db.users.find(
                        {
                            "invited_by": str(inv),
                            "invite_type": {"$exists": True}
                        },
                        {
                            "invite_code": True,
                            "invite_type": True,
                            "joined_at": True,
                            "invited_by": True
                        }
                ):
                    regular += 1
                    if invite['invite_type'] == InviteType.FAKE.value:
                        regular -= 1
                    elif invite['invite_type'] == InviteType.LEAVE.value:
                        regular -= 1

                    invite.inviter = get(member.guild.members, id=int(invite['invited_by']))

                # TODO usuń poprzednie role, jeśli dałeś nową
                # TODO przy wychodzeniu użytkownika również sprawdzaj czy wypada zabrać/dać role


                if regular >= 2048:
                    await invite.inviter.add_roles(boost2048_invite)

                elif regular >= 1024:
                    await invite.inviter.add_roles(boost1024_invite)

                elif regular >= 512:
                    await invite.inviter.add_roles(boost512_invite)

                elif regular >= 256:
                    await invite.inviter.add_roles(boost256_invite)

                elif regular >= 128:
                    await invite.inviter.add_roles(boost128_invite)

                elif regular >= 64:
                    await invite.inviter.add_roles(boost64_invite)

                elif regular >= 16:
                    await invite.inviter.add_roles(boost16_invite)

                elif regular >= 8:
                    await invite.inviter.add_roles(boost8_invite)

                elif regular >= 4:
                    await invite.inviter.add_roles(boost4_invite)

                elif regular >= 2:
                    await invite.inviter.add_roles(boost2_invite)

                return

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        channel = self.client.get_channel(member_leave_logs_channel)
        info = await self.client.db.users.find_one(
            {"_id": str(member.id)}, {"invited_by": 1}
        )
        if not info:
            info = {}

        inv = info.get('invited_by')

        await channel.send(
            embed=Embed(
                title=str(member),
                color=Colour.red(),
                description=f"Wyszedł {member.mention} zaproszony przez <@{inv}> ({inv})"
            ).set_thumbnail(url=str(member.avatar_url_as(format="png"))).set_footer(text=member.id)
        )
        await self.client.db.users.update_one(
            {"_id": str(member.id)}, {"$set": {
                "invite_type": InviteType.LEAVE.value
            }}, upsert=True
        )

    @commands.Cog.listener()
    async def on_invite_create(self, invite: Invite):
        await self.client.db.invites.update_one(
            {"_id": invite.code}, {"$set": {"uses": invite.uses}}, upsert=True
        )

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.client.db.invites.delete_one(
            {"_id": invite.code}
        )


def setup(client):
    client.add_cog(Zaproszenia(client))
