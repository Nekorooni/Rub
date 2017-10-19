import datetime
from collections import defaultdict
from enum import Enum

import discord
from discord.ext import commands


def exp_needed(level):
    return 50 + round(5 * (level ** 2) - (5 * level))


def total_exp(level):
    i = 0
    for l in range(1, level - 1):
        i += exp_needed(l)
    return i


class Gains(Enum):
    message = 10
    attachment = 5


class Level:
    """A cog for checking activity in the form of experience"""

    def __init__(self, bot):
        self.bot = bot
        self.ch = None

    async def on_ready(self):
        self.ch = self.bot.get_channel(344104210406834176)

    async def on_message(self, msg):
        if not msg.guild:
            return
        if msg.author == self.bot.user:
            return
        if msg.guild.id != 320567296726663178:
            return
        f = await self.bot.db.fetchone(f'SELECT `level`, `exp`, `ts` FROM levels WHERE user_id={msg.author.id}')
        if not f:
            f = await self.bot.db.fetchone(f'INSERT INTO levels VALUES ({msg.author.id}, 1, 0, "{msg.created_at}")')
        l, x, t = f
        d = abs(msg.created_at - t)
        if d < datetime.timedelta(seconds=20):
            return
        x += 10
        needed = exp_needed(l)
        if x >= needed:
            l += 1
            x -= needed
            await self.ch.send(f'{msg.author} leveled up to {l}!')
            if l == 10:
                await msg.author.add_roles(discord.utils.get(msg.guild.roles, name='Neko'))
        await self.bot.db.execute(f'UPDATE levels SET level={l}, exp={x}, ts="{msg.created_at}" WHERE user_id={msg.author.id}')

    @commands.command()
    async def rank(self, ctx):
        peeps = await ctx.bot.db.fetch('SELECT user_id, level, exp FROM levels ORDER BY level DESC, exp DESC LIMIT 10')
        output = '```'
        await ctx.send(
            '```'+'\n'.join([f'{i+1} - {ctx.guild.get_member(p[0]).name}' for i, p in enumerate(peeps) if ctx.guild.get_member(p[0])])+'```')


    @commands.command()
    @commands.guild_only()
    async def profile(self, ctx, member: discord.Member=None):
        if not member:
            member = ctx.author
        l, x = await self.bot.db.fetchone(f"SELECT `level`, `exp` FROM levels WHERE user_id={member.id}")
        data = {
            "thumbnail": {
              "url": f"{member.avatar_url}"
            },
            "author": {
              "name": f"{member}"
            },
            "fields": [
              {
                "name": "Level",
                "value": f"{l}",
                "inline": True
              },
              {
                "name": "Experience",
                "value": f"{x} / {exp_needed(l)}",
                "inline": True
              }
            ]
          }
        await ctx.send(embed=discord.Embed().from_data(data))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def store_db(self, ctx):
        from collections import defaultdict
        import datetime
        data = defaultdict(lambda: [1, 0, datetime.datetime.now() - datetime.timedelta(days=365)])
        for channel in ctx.guild.channels:
            if not isinstance(channel, discord.TextChannel):
                continue
            messages = await channel.history(limit=20000, reverse=True).flatten()
            messages.sort(key=lambda r: r.created_at)
            for msg in messages:
                l, x, t = data[msg.author.id]
                d = abs(msg.created_at - t)
                if d < datetime.timedelta(seconds=60):
                    continue
                x += 10
                needed = exp_needed(l)
                if x >= needed:
                    l += 1
                    x -= needed
                data[msg.author.id] = l, x, msg.created_at
        for k, v in data.items():
            await ctx.bot.db.execute(
                f'INSERT INTO levels (user_id, level, exp, ts) VALUES ({k}, {v[0]}, {v[1]}, "{v[2]}")'
            )


def setup(bot):
    bot.add_cog(Level(bot))
