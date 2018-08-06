import asyncio
import datetime
from .utils import time
from discord.ext import commands
import discord

EXCLUDED_CHANNELS = [
    362669211966767104,  # Ask-rub
    371046668856197131,  # Snackbox
]


def exp_needed(level):
    return round(20 * level ** 1.05)


def exp_total(level):
    return sum([exp_needed(x) for x in range(level + 1)])


class Profiles:
    """Stuff for profiles"""

    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    async def get_experience(self, user_id):
        level, exp = await self.bot.redis.hmget(f'profile:{user_id}', 'level', 'exp')
        if not level:
            await self.bot.redis.hmset(f'profile:{user_id}', 'level', 1, 'exp', 0)
            return 1, 0
        return int(level), int(exp)

    async def give_experience(self, user_id, amount=10):
        level, exp = await self.get_experience(user_id)
        exp += amount

        # Level up to 5 times at once
        for i in range(5):
            needed = exp_needed(level)
            if exp >= needed:
                level += 1
                exp -= needed

                if level

                continue
            break
        await self.bot.redis.hmset(f'profile:{user_id}', 'level', level, 'exp', exp)

    async def on_message(self, msg):
        if not msg.guild:
            return
        if msg.channel.id in EXCLUDED_CHANNELS:
            return
        if msg.author.bot:
            return

        d = abs(msg.created_at - self.cooldowns.get(msg.author.id, datetime.datetime(2000, 1, 1)))
        if d < datetime.timedelta(seconds=30):
            return

        await self.give_experience(msg.author.id)

        self.cooldowns[msg.author.id] = msg.created_at

    @commands.command()
    async def profile(self, ctx):
        """Display your profile"""
        member = ctx.author
        e = discord.Embed(title=member.display_name)
        e.set_thumbnail(url=member.avatar_url_as(size=128))
        e.add_field(name=f'Created', value=time.time_ago(member.created_at), inline=True)
        if ctx.guild:
            e.add_field(name=f'Joined', value=time.time_ago(member.joined_at), inline=True)
            e.add_field(name=f'Nickname', value=member.nick or "None", inline=False)
            e.add_field(name=f'Roles', value=' '.join([role.mention for role in member.roles[:0:-1]]), inline=False)

            role = self.get_top_color(member.roles) if ctx.guild else None
            if role:
                e.colour = role.color
        await ctx.send(embed=e)

    @commands.command(aliases=['experience'])
    async def xp(self, ctx, *, member: discord.Member = None):
        """Shows your exp"""
        if not member:
            member = ctx.author

        level, exp = await self.get_experience(member.id)
        em = discord.Embed(title=f'{member.display_name}')
        em.add_field(name="Level", value=f'**{level}**')
        em.add_field(name="Exp", value=f'{exp}/{exp_needed(level)}xp')
        em.set_thumbnail(url=member.avatar_url_as(size=64))

        role = self.get_top_color(member.roles)
        if role:
            em.colour = role.color

        await ctx.send(embed=em)

    def get_top_color(self, roles):
        excluded = ['Neko', 'Rare Neko']
        for role in roles[::-1]:
            if role.color != discord.Colour.default() and role.name not in excluded:
                return role
        return None


def setup(bot):
    bot.add_cog(Profiles(bot))
