import discord
from discord.ext import commands

class Monitor:
    """Monitoring the world"""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    async def on_message_delete(self, message):
        att = '\n'.join(x.url for x in message.attachments)
        await self.bot.db.execute(f'INSERT INTO `monitorlog` (`type`, `author`, `content`, `attachments`) '
                                  f'VALUES ("delete",{message.author.id}, "{message.content}", "{att}")')

def setup(bot):
    bot.add_cog(Monitor(bot))
