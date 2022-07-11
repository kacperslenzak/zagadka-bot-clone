import discord


class HelpEmbed:
    def __init__(self, context):
        self.color = discord.Colour.from_rgb(0, 0, 0)
        self.embed = discord.Embed(color=self.color)
        self.context = context

    def create(self):
        self.embed.add_field(name="view permission", value=f"?view - {self.context.author.mention}", inline=True)
        self.embed.add_field(name="speak permission", value=f"?speak - {self.context.author.mention}", inline=True)
        self.embed.add_field(name="reset permission", value=f"?reset - {self.context.author.mention}", inline=True)
        self.embed.add_field(name="global connect permission", value=f"?connect - ", inline=True)
        self.embed.add_field(name="global view permission", value=f"?view - ", inline=True)
        self.embed.add_field(name="global speak permission", value=f"?speak - ", inline=True)
        self.embed.add_field(name="reset global permissions", value=f"?reset", inline=True)
        self.embed.add_field(name="user limit", value=f"?limit 2", inline=True)
        self.embed.add_field(name="current channel", value=f"?vc", inline=True)
        self.embed.set_footer(text="to allow permission use +")

    def add_field(self, name, value, inline):
        self.embed.add_field(name=name, value=value, inline=inline)

    def to_dict(self):
        return self.embed.to_dict()
