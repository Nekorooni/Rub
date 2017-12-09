import datetime

import asyncio
import discord
from discord.ext import commands

GUILD_ID = 320567296726663178
LOG_CHANNEL = 383059844803985408


async def poll_audit_log(guild, action, after, *, poll=1, **kwargs):
    print(f"Polling for {action}")
    print(f"After: {after}")
    for i in range(poll):
        print(f"Poll {i+1}")
        log = await guild.audit_logs(action=action, after=after).get(**kwargs)
        if log:
            print(f"Found audit log")
            print(log)
            return log
        await asyncio.sleep(1)
    print(f"Didn't find anything")
    return None


class Stafflog:

    def __init__(self, bot):
        self.bot = bot

    async def post_event(self, *, title=None, desc=None, footer=None, color=discord.Colour.default()):
        e = discord.Embed(title=title, description=desc, color=color)
        if footer:
            e.set_footer(text=footer)
        await self.bot.get_channel(LOG_CHANNEL).send(embed=e)

    async def on_member_join(self, member):
        now = datetime.datetime.utcnow()
        days, r = divmod((now-member.created_at).total_seconds(), 86400)
        h, r = divmod(r, 3600)
        m, s = divmod(r, 60)
        e = discord.Embed(title=f'{member} joined', description=f'Made {days} days {h:02d}:{m:02d}:{s:02d} ago',
                          color=discord.Colour.green())
        e.set_thumbnail(url=member.avatar_url)
        e.set_footer(text=member.id)
        e.timestamp = now
        await self.bot.get_channel(LOG_CHANNEL).send(embed=e)

    async def on_member_ban(self, guild, member):
        print('On member ban')
        print(datetime.datetime.utcnow())

    async def on_member_remove(self, member):
        print('On member remove')
        print(datetime.datetime.utcnow())
        if member.guild.id != GUILD_ID:
            return
        time = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        l = await poll_audit_log(member.guild, discord.AuditLogAction.kick, time, poll=2, target__id=member.id)
        if l:
            return await self.bot.get_channel(LOG_CHANNEL).send(f'{member} kicked for {l.reason}')
        l = await poll_audit_log(member.guild, discord.AuditLogAction.ban, time, target__id=member.id)
        if l:
            u = await poll_audit_log(member.guild, discord.AuditLogAction.unban, time, target__id=member.id)
            if u:
                return await self.bot.get_channel(LOG_CHANNEL).send(f'{member} softbanned for {l.reason}')
            else:
                return await self.bot.get_channel(LOG_CHANNEL).send(f'{member} banned for {l.reason}')
        return await self.bot.get_channel(LOG_CHANNEL).send(f'{member} left')

    async def on_member_unban(self, guild, member):
        if guild.id != GUILD_ID:
            return
        time = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        l = await poll_audit_log(guild, discord.AuditLogAction.unban, time, poll=2, target__id=member.id)
        if l:
            return await self.bot.get_channel(LOG_CHANNEL).send(f'{member} unbanned for {l.reason}')


def setup(bot):
    bot.add_cog(Stafflog(bot))
