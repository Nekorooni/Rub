import datetime
from collections import defaultdict
from discord.ext import commands
import discord

def exp_needed(level):
    return 50 + round(5 * (level ** 2) - (5 * level))


def needs_profile(**kwargs):
    async def predicate(ctx):
        if ctx.guild is None:
            return False

        cog = ctx.bot.get_cog('Profiles')

        ctx.profile = await cog.get_profile(ctx.author.id, **kwargs)

        return True
    return commands.check(predicate)

class Profile:
    __slots__ = ('pid', 'level', 'experience', 'coins')

    def __init__(self, profile_id, level, experience, coins):
        self.pid = profile_id
        self.level = level
        self.experience = experience
        self.coins = coins

    async def save(self, db):
        qry = f'UPDATE `profiles` SET level={self.level}, experience={self.experience}, coins={self.coins} ' \
              f'WHERE id={self.pid}'
        await db.execute(qry)


class Profiles:
    """Stuff for profiles"""

    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    async def get_profile(self, user_id, **kwargs):
        profile = await self.bot.db.fetchone(f'SELECT `id`, `level`, `experience`, `coins` '
                                             f'FROM `profiles` WHERE user_id={user_id}')
        if not profile:
            r, i = await self.bot.db.execute(f'INSERT INTO `profiles` (`user_id`) VALUES ({user_id})')
            if r:
                return Profile(i, 1, 0, 500)
            else:
                raise commands.CommandError
        return Profile(*profile)

    async def on_message(self, msg):
        if not msg.guild:
            return
        if msg.guild.id != 320567296726663178:
            return
        if msg.author.bot:
            return
        profile = await self.get_profile(msg.author.id)
        d = abs(msg.created_at - self.cooldowns.get(profile.pid, datetime.datetime(2000, 1, 1)))
        if d < datetime.timedelta(seconds=20):
            return
        profile.experience += 10
        needed = exp_needed(profile.level)
        if profile.experience >= needed:
            profile.level += 1
            profile.experience -= needed
            if profile.level == 3:
                await msg.author.add_roles(discord.utils.get(msg.guild.roles, name='Neko'))
        await profile.save(self.bot.db)
        self.cooldowns[profile.pid] = msg.created_at

    @commands.command()
    @needs_profile()
    async def xp(self, ctx):
        await ctx.send(f'Lv{ctx.profile.level} {ctx.profile.experience}xp')

    @commands.command()
    @needs_profile(coins=True)
    async def coins(self, ctx, member: discord.Member=None):
        if member:
            ctx.profile = await self.get_profile(member.id)
        await ctx.send(f'You have {ctx.profile.coins} coins')

def setup(bot):
    bot.add_cog(Profiles(bot))
