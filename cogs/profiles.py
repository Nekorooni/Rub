import datetime
import random

import aiohttp
import asyncio
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

        if ctx.invoked_with.lower() == 'help':
            return True

        cog = ctx.bot.get_cog('Profiles')
        async with ctx.typing():
            ctx.profile = await cog.get_profile(ctx.author.id, keys)

        return True
    return commands.check(predicate)


class Profile:
    __slots__ = ('user_id', 'level', 'experience', 'fame', 'coins')

    def __init__(self, uid, **kwargs):
        self.user_id = uid
        self.level = kwargs.get('level', 1)
        self.experience = kwargs.get('experience', 1)
        self.coins = kwargs.get('coins', 1)

    async def save(self, db):
        s = ','.join([f'{s}={getattr(self,s,None)}' for s in self.__slots__[1:] if getattr(self, s, None) is not None])
        await db.execute(f"UPDATE profiles SET {s} WHERE user_id={self.user_id}")

    async def has_item(self, name=None):
        pass

class Profiles:
    """Stuff for profiles"""

    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self._lock = asyncio.Lock(loop=bot.loop)

    async def get_profile(self, uid, keys=None):
        s = ', '.join(keys)
        profile = await self.bot.db.fetchdict(f'SELECT {s or "*"} FROM profiles WHERE user_id={uid}')
        if not profile:
            await self.bot.db.execute(f'INSERT INTO profiles (user_id, coins) VALUES (%s, %s)', (uid, 500))
            return Profile(uid, level=1, experience=0, coins=500)
        return Profile(uid, **profile)

    async def on_message(self, msg):
        if not msg.guild:
            return
        if msg.channel.id in EXCLUDED_CHANNELS:
            return
        if msg.author.bot:
            return

        async with self._lock:
            profile = await self.get_profile(msg.author.id, ('level', 'experience', 'coins'))

            d = abs(msg.created_at - self.cooldowns.get(profile.user_id, datetime.datetime(2000, 1, 1)))
            if d < datetime.timedelta(seconds=30):
                return

            profile.experience += 10
            needed = exp_needed(profile.level)

            # Terrible temporary levelup
            if profile.experience >= needed:
                profile.level += 1
                profile.experience -= needed
                profile.coins += random.randint(1, 10)

            await profile.save(self.bot.db)
            self.cooldowns[profile.user_id] = msg.created_at

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        p = await self.get_profile(member.id, ('level', 'experience'))
        em = discord.Embed(title=f'{member}',
                           description=f'**Lv{p.level}** {p.experience}/{exp_needed(p.level)}xp')
        await ctx.send(embed=em)

    @commands.command(aliases=['experience'])
    async def xp(self, ctx, member: discord.Member=None):
        """Shows your exp"""
        if not member:
            member = ctx.author
        p = await self.get_profile(member.id, ('level', 'experience'))
        em = discord.Embed(title=f'{member.display_name}', colour=0x77dd77)
        em.add_field(name="Level", value=f'**{p.level}**')
        em.add_field(name="Exp", value=f'{p.experience}/{exp_needed(p.level)}xp')
        em.set_thumbnail(url=member.avatar_url_as(size=64))
        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def coins(self, ctx, member: discord.Member = None):
        if ctx.invoked_subcommand is not None:
            return
        if member:
            ctx.profile = await self.get_profile(member.id, ['coins'])
            em = discord.Embed(description=f'{member} has {ctx.profile.coins} coins')
        else:
            ctx.profile = await self.get_profile(ctx.author.id, ['coins'])
            em = discord.Embed(description=f'You have {ctx.profile.coins} coins')
        await ctx.send(embed=em)

    @coins.command()
    @commands.has_role('Admin')
    async def give(self, ctx, member: discord.Member, amount: int):
        ctx.profile = await self.get_profile(member.id, ['coins'])
        ctx.profile.coins += amount
        await ctx.profile.save(self.bot.db)
        await ctx.send(f"Gave {amount} to {member}, they now have {ctx.profile.coins}")

    @coins.command()
    @commands.has_role('Admin')
    async def take(self, ctx, member: discord.Member, amount: int):
        ctx.profile = await self.get_profile(member.id, ['coins'])
        if ctx.profile.coins >= amount:
            ctx.profile.coins -= amount
            await ctx.profile.save(self.bot.db)
            await ctx.send(f"Took {amount} from {member}, they now have {ctx.profile.coins}")
        else:
            await ctx.send(f"{member} would be in debt.")

    @commands.group(aliases=['inv'])
    async def inventory(self, ctx, member: discord.Member = None):
        if member:
            ctx.profile = await self.get_profile(member.id)
        items = await ctx.bot.db.fetch(f'SELECT it.name, data FROM inventory '
                                       f'INNER JOIN items it ON item_id=it.id '
                                       f'WHERE user_id=%s', (ctx.author.id,))
        if items:
            await ctx.send('\n'.join([f'{data+" " if data else ""}{name}' for name, data in items]))
        else:
            await ctx.send("You don't have anything.")

    @commands.command(aliases=['color'])
    async def colour(self, ctx, *, colour):
        """Change your color using colour coupons"""
        role = discord.utils.get(ctx.guild.roles, name=colour)

        if role:
            pass
        else:
            await ctx.send("I don't know that colour. Did you type it right?")


def setup(bot):
    bot.add_cog(Profiles(bot))
