import heapq
from collections import Counter

import datetime

import collections
from operator import itemgetter

from discord.ext import commands

import discord
import random


def get_color_role(member):
    for role in member.roles:
        if role.color == member.color:
            return role


class Helpful:
    """Random helpful commands"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """Show someones avatar."""
        if not user:
            user = ctx.author
        await ctx.send(user.avatar_url)

    @commands.command()
    async def ping(self, ctx):
        t = datetime.datetime.utcnow() - ctx.message.created_at
        await ctx.send(f'pong :v *{t.total_seconds()}*')

    @commands.command()
    async def color(self, ctx, color: discord.Colour):
        if ctx.guild.id != 352672918473277440:
            return
        role = await ctx.guild.create_role(name=str(color), colour=color)
        await ctx.author.remove_roles(get_color_role(ctx.author))
        await ctx.author.add_roles(role)
        await ctx.guild.me.add_roles(role)
        await ctx.guild.me.remove_roles(get_color_role(ctx.guild.me))
        await ctx.send(str(color))

    @commands.command()
    async def get_active(self, ctx, limit=100):
        members = []
        channel = self.bot.get_channel(320567296726663178)
        async for m in channel.history(limit=limit):
            if m.author not in members:
                members.append(m.author)
        random.shuffle(members)
        await ctx.send('\n'.join([f"{i} - {x.name}" for i, x in enumerate(members)]))

def setup(bot):
    bot.add_cog(Helpful(bot))
