import discord
from discord import Attachment, AllowedMentions, File
from discord.ext import commands
from asyncio import sleep
import io

from PIL import Image


def generate_img(picture) -> io.BytesIO:
    mem = Image.open(io.BytesIO(picture), formats=['JPEG', 'PNG']).convert('RGBA')
    watermark = Image.open('watermark.png').convert('RGBA')

    w = int(mem.width * 0.2)
    h = int((watermark.height * w) / watermark.width)

    watermark = watermark.resize((w, h))

    mem.paste(watermark, (mem.width - w, mem.height - h), watermark)

    result = io.BytesIO()
    mem.save(result, "PNG")
    result.seek(0)

    return result


class ImageWatermark(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if len(message.attachments) == 0:
            return

        attachments = []
        for attachment in message.attachments:
            if attachment.content_type not in ('image/png', 'image/jpg', 'image/jpeg'):
                return

            watermark_data = generate_img(await attachment.read())
            attachments.append(File(watermark_data, attachment.filename))

        try:
            await message.delete()
        except:
            return

        webhook = await message.channel.webhooks()
        if not webhook:
            webhook.append(await message.channel.create_webhook(name='Image Webhook'))

        webhook = webhook[0]

        kwargs = dict(
            content=message.content or None,
            tts=message.tts,
            files=attachments
        )

        await webhook.send(
            username=message.author.name,
            avatar_url=message.author.avatar_url_as(),
            **kwargs
        )


def setup(client):
    client.add_cog(ImageWatermark(client))
