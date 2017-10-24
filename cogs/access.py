import discord
from discord.ext import commands


class Access:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['grant'])
    async def permit(self, ctx, member: discord.Member, channel: discord.TextChannel=None):
        """Permit someone access to a channel"""
        if not channel:
            channel = ctx.channel
        await channel.set_permissions(member, read_messages=True)


def setup(bot):
    bot.add_cog(Access(bot))
