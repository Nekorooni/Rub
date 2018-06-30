import asyncio
import datetime
import random
from .utils import time
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
    return sum([exp_needed(x) for x in range(level + 1)])


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
        self.level = kwargs.get('level')
        self.experience = kwargs.get('experience')
        self.coins = kwargs.get('coins')

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
        self._locks = dict()

    def get_lock(self, name):
        lock = self._locks.get(name)
        if not lock:
            lock = asyncio.Lock(loop=self.bot.loop)
            self._locks[name] = lock
        return lock

    async def get_profile(self, uid, keys=None):
        s = ', '.join(keys)
        profile = await self.bot.db.fetchdict(f'SELECT * FROM profiles WHERE user_id={uid}')
        if not profile:
            await self.bot.db.execute('INSERT INTO profiles (user_id,level,experience,coins) VALUES (%s,%s,%s,%s)',
                                      (uid, 1, 0, 100))
            return Profile(uid, level=1, experience=0, coins=100)
        return Profile(uid, **profile)

    async def on_message(self, msg):
        if not msg.guild:
            return
        if msg.channel.id in EXCLUDED_CHANNELS:
            return
        if msg.author.bot:
            return
        async with self.get_lock(msg.author.id):
            profile = await self.get_profile(msg.author.id, ('level', 'experience', 'coins'))

            d = abs(msg.created_at - self.cooldowns.get(profile.user_id, datetime.datetime(2000, 1, 1)))
            if d < datetime.timedelta(seconds=30):
                return

            profile.experience += 10

            self.cooldowns[profile.user_id] = msg.created_at

            needed = exp_needed(profile.level)

            # Terrible temporary levelup
            if profile.experience >= needed:
                profile.level += 1
                profile.experience -= needed
                profile.coins += 10

            await profile.save(self.bot.db)

    @commands.command()
    async def profile(self, ctx):
        """Display your profile"""
        member = ctx.author
        e = discord.Embed(title=member.display_name)
        e.set_thumbnail(url=member.avatar_url_as(size=128))
        e.add_field(name=f'Created', value=time.time_ago(member.created_at), inline=True)
        if ctx.guild:
            if member.id == 73389450113069056:
                member.joined_at = ctx.guild.created_at
            e.add_field(name=f'Joined', value=time.time_ago(member.joined_at), inline=True)
            e.add_field(name=f'Nickname', value=member.nick or "None", inline=False)
            e.add_field(name=f'Roles', value=' '.join([role.mention for role in member.roles[:0:-1]]), inline=False)

            role = self.get_top_color(member.roles) if ctx.guild else None
            if role:
                e.colour = role.color
        await ctx.send(embed=e)

    @commands.command(hidden=True)
    async def rank(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        qry = f"""
        select `level`, `experience`, `rank` FROM
        (
        select t.*, @r := @r + 1 as `rank`
        from  profiles t,
        (select @r := 0) r
        order by `level` desc, `experience` desc
        ) as t
        where `user_id`={member.id}
        """
        lvl, xp, rank = await ctx.bot.db.fetchone(qry)
        em = discord.Embed(title=f'**{member.display_name}**', color=0x77dd77,
                           description=f'**Rank {round(rank)} - Lv{lvl}** {xp}/{exp_needed(lvl)}xp')
        await ctx.send(embed=em)

    @commands.command(hidden=True, aliases=['leaderboards', 'ranks', 'rankings'])
    async def leaderboard(self, ctx, page: int = 1):
        guild = self.bot.get_guild(215424443005009920)
        qry = f"""
        select `user_id`, `level`, `experience`, `rank` FROM
        (
        select t.*, @r := @r + 1 as `rank`
        from  profiles t,
        (select @r := 0) r
        order by `level` desc, `experience` desc
        ) as t
        limit %s, %s
        """
        r = await ctx.bot.db.fetch(qry, ((page - 1) * 10, 10))
        w = max(len(getattr(guild.get_member(user_id), 'display_name', 'user_left')) for user_id, lvl, xp, rank in r)
        output = '```\n' + '\n'.join([
                                         f"{int(rank):<3} - {getattr(guild.get_member(user_id),'display_name','user_left'):<{w}} - Lv{lvl:<4} {xp:<5} / {exp_needed(lvl):>5}xp"
                                         for user_id, lvl, xp, rank in r]) + '```'
        await ctx.send(output)

    @commands.command(aliases=['experience'])
    async def xp(self, ctx, *, member: discord.Member = None):
        """Shows your exp"""
        if not member:
            member = ctx.author

        async with self.get_lock(member.id):
            p = await self.get_profile(member.id, ('level', 'experience'))
            em = discord.Embed(title=f'{member.display_name}')
            em.add_field(name="Level", value=f'**{p.level}**')
            em.add_field(name="Exp", value=f'{p.experience}/{exp_needed(p.level)}xp')
            em.set_thumbnail(url=member.avatar_url_as(size=64))

            role = self.get_top_color(member.roles)
            if role:
                em.colour = role.color

            await ctx.send(embed=em)

    def get_top_color(self, roles):
        excluded = ['Muted', 'Guardian Angel']
        for role in roles[::-1]:
            if role.color != discord.Colour.default() and role.name not in excluded:
                return role
        return None


def setup(bot):
    bot.add_cog(Profiles(bot))
