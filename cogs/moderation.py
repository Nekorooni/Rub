from discord.ext import commands

import asyncio
import discord
import random

class Moderation:
    """Moderation commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await ctx.guild.kick(member, reason=reason)
            await ctx.message.add_reaction('hqcaramel:361532992499220492')
        except:
            await ctx.message.add_reaction('tsumikuBlank:364178887917436933')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await ctx.guild.ban(member, reason=reason)
            await ctx.message.add_reaction('hqcaramel:361532992499220492')
        except:
            await ctx.message.add_reaction('tsumikuBlank:364178887917436933')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await ctx.guild.ban(member, reason=reason)
            await ctx.guild.unban(member, reason='Softban')
            await ctx.message.add_reaction('hqcaramel:361532992499220492')
        except:
            await ctx.message.add_reaction('tsumikuBlank:364178887917436933')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, *params):
        data={}
        for k in iter(params):
            data[k] = discord.Object(id=next(k))
        await ctx.channel.purge(limit=100, **data)


def setup(bot):
    bot.add_cog(Moderation(bot))
