import datetime

import discord
from discord.ext import commands

GUILD_ID = 320567296726663178
LOG_CHANNEL = 383059844803985408


class Stafflog:

    def __init__(self, bot):
        self.bot = bot

    async def post_event(self, *, title=None, desc=None, footer=None, color=discord.Colour.default()):
        e = discord.Embed(title=title, description=desc, color=color)
        if footer:
            e.set_footer(text=footer)
        await self.bot.get_channel(LOG_CHANNEL).send(embed=e)

    async def on_member_join(self, member):
        if member.guild.id != GUILD_ID:
            return
        creation = datetime.datetime.utcnow()-member.created_at
        days, seconds = creation.days, creation.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        e = discord.Embed(title=f"{member} joined",
                          description=f'Created {days} days, {hours} hours, {minutes} minutes ago', color=0x6cdb81)
        e.set_footer(text=f'{member.id}')
        e.set_thumbnail(url=member.avatar_url_as(size=64))
        e.timestamp = datetime.datetime.utcnow()
        await self.bot.get_channel(LOG_CHANNEL).send(embed=e)

    async def on_member_remove(self, member):
        if member.guild.id != GUILD_ID:
            return
        await self.post_event(title=f"{member} ({member.id}) left", color=0xdb6c79)

    async def on_member_ban(self, guild, user):
        if guild.id != GUILD_ID:
            return
        await self.post_event(title=f"{user} (*{user.id}*) banned", color=0xd23838)

    async def on_member_kick(self, guild, user):
        if guild.id != GUILD_ID:
            return
        await self.post_event(title=f"{user} ({user.id}) kicked", color=0xd28838)


def setup(bot):
    bot.add_cog(Stafflog(bot))
