from discord.ext import commands


class Memes:
    """The stupid shit goes here."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def petah(self, ctx, num: int = 10):
        """Reacts to messages with :petah:"""
        async for msg in ctx.history(limit=num):
            await msg.add_reaction('petah:316578038626385950')


def setup(bot):
    bot.add_cog(Memes(bot))
