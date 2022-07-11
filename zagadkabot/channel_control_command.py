import discord


async def channel_command(ctx, command, *args):
    author: discord.Member = ctx.author
    vc: discord.VoiceState = author.voice

    if not vc or not vc.channel:
        return

    if not author.permissions_in(vc.channel).priority_speaker:
        return

    channel: discord.VoiceChannel = vc.channel

    if command in ('connect', 'view', 'speak'):
        if args[0] == '+':
            action = True
        elif args[0] == '-':
            action = False
        else:
            return

        if args[1] in (None, 'everyone', 'here', '@here'):
            subject = channel.guild.default_role
        else:
            subject = args[1]

        overwrite = channel.overwrites_for(subject)
        if overwrite is None:
            overwrite = discord.PermissionOverwrite()

        if command == "connect":
            overwrite.connect = action
            if action is False and isinstance(subject,
                                              discord.Member) and subject.voice and subject.voice.channel == channel:
                await subject.move_to(None)
            await channel.set_permissions(subject, overwrite=overwrite, reason=f"{author}")
        elif command == "view":
            overwrite.view_channel = action
            await channel.set_permissions(subject, overwrite=overwrite, reason=f"{author}")
        elif command == "speak":
            overwrite.speak = action
            if isinstance(subject, discord.Member) and subject.voice and subject.voice.channel == channel:
                await subject.edit(voice_channel=ctx.guild.afk_channel)
                await subject.edit(voice_channel=channel)
            await channel.set_permissions(subject, overwrite=overwrite, reason=f"{author}")
        else:
            return

    elif command == "limit":
        await channel.edit(user_limit=args[0], reason=f"Limit changed by {author}")

    elif command == "reset":
        if len(args) == 0:
            await channel.edit(user_limit=0, sync_permissions=True, reason=f"Reset permissions by {author}")
            await channel.set_permissions(author, speak=True, connect=True, priority_speaker=True,
                                          reason=f"Reset permissions by {author}")
            return

        if args[0] in (None, "everyone", "@everyone", "here", "@here"):
            await channel.edit(sync_permissions=True, reason=f"Reset permissions by {author}")
            await channel.set_permissions(author, speak=True, connect=True, priority_speaker=True,
                                          reason=f"Reset permissions by {author}")
            return

        await channel.set_permissions(args[0], overwrite=None, reason=f"{author}")
    else:
        return
