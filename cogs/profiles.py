import datetime
import random
from collections import defaultdict

import aiohttp
from discord.ext import commands
import discord

EXCLUDED_CHANNELS = [
    362669211966767104,  # Ask-rub
    371046668856197131,  # Snackbox
    370941450361372672,  # Yui-Roo
]

def exp_needed(level):
    return round(20 * level ** 1.05)


def exp_total(level):
    return sum([exp_needed(x) for x in range(level+1)])


def needs_profile(keys=None):
    async def predicate(ctx):
        if ctx.guild is None:
            return False

        cog = ctx.bot.get_cog('Profiles')
        async with ctx.typing():
            ctx.profile = await cog.get_profile(ctx.author.id, keys)

        return True
    return commands.check(predicate)


class PartialProfile:
    __slots__ = ('pid', 'level', 'experience', 'coins')

    def __init__(self, pid, **kwargs):
        self.pid = pid
        for k in kwargs:
            setattr(self, k, kwargs[k])

    async def save(self, db):
        s = ', '.join([f'{s}={getattr(self,s,None)}' for s in self.__slots__[1:] if getattr(self, s, None) is not None])
        await db.execute(f"UPDATE profiles SET {s} WHERE id={self.pid}")


class Profiles:
    """Stuff for profiles"""

    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.profiles = {}

    async def get_profile(self, u_id, keys=None):
        if u_id in self.profiles:
            p_id = self.profiles[u_id]
        else:
            p_id, = await self.bot.db.fetchone(f'SELECT id FROM profiles WHERE user_id={u_id}') or (None,)
            if not p_id:
                _, p_id = await self.bot.db.execute(f'INSERT INTO profiles (user_id) VALUES ({u_id})')
            self.profiles[u_id] = p_id
        if keys:
            s = ', '.join(keys)
            data = await self.bot.db.fetchone(f'SELECT {s} FROM profiles WHERE id={p_id}', assoc=True)
            return PartialProfile(p_id, **data)
        return PartialProfile(p_id)

    async def on_message(self, msg):
        if not msg.guild:
            return
        if msg.guild.id != 320567296726663178:
            return
        if msg.channel.id in EXCLUDED_CHANNELS:
            return
        if msg.author.bot:
            return
        profile = await self.get_profile(msg.author.id, ('level', 'experience', 'coins'))
        d = abs(msg.created_at - self.cooldowns.get(profile.pid, datetime.datetime(2000, 1, 1)))
        if d < datetime.timedelta(seconds=20):
            return
        profile.experience += 10
        profile.coins += 1
        needed = exp_needed(profile.level)
        if profile.experience >= needed:
            profile.level += 1
            profile.experience -= needed
            if profile.level == 3:
                await msg.author.add_roles(discord.utils.get(msg.guild.roles, name='Neko'))
        await profile.save(self.bot.db)
        self.cooldowns[profile.pid] = msg.created_at

    @commands.command()
    async def xp(self, ctx, member: discord.Member=None):
        if not member:
            member = ctx.author
        p = await self.get_profile(member.id, ('level', 'experience'))
        em = discord.Embed(title=f'**{member}**',
                           description=f'**Lv{p.level}** {p.experience}/{exp_needed(p.level)}xp')
        await ctx.send(embed=em)

    @commands.command()
    @needs_profile(['coins'])
    async def coins(self, ctx, member: discord.Member = None):
        if member:
            ctx.profile = await self.get_profile(member.id, ['coins'])
            em = discord.Embed(description=f'{member} has {ctx.profile.coins} coins')
        else:
            em = discord.Embed(description=f'You have {ctx.profile.coins} coins')
        await ctx.send(embed=em)
        
    @commands.command()
    @needs_profile()
    async def inv2(self, ctx):
        items = await ctx.bot.db.fetch(f'SELECT it.name, it.shortdesc, data FROM inventory '
                                       f'INNER JOIN items it ON item_id=it.id WHERE profile_id={ctx.profile.pid} '
                                       f'LIMIT 10')
        embeds = [discord.Embed.from_data({'title': f'{n} `{d}`', 'color': random.randrange(1, 16777215)}) for n, s, d in items]
        async with aiohttp.ClientSession() as session:
            hook = discord.Webhook.from_url('https://canary.discordapp.com/api/webhooks/380881003159486465/hF1rfRXZYReBP2WjgavnrYHQuXKU6joN4aBPsfsaWszqUzFY5I8RmwMyIhGDG2eOH-n5', adapter=discord.AsyncWebhookAdapter(session))
            await hook.send(embeds=embeds)

def setup(bot):
    bot.add_cog(Profiles(bot))
