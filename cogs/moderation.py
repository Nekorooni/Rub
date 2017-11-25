from discord.ext import commands

import asyncio
import discord
import random

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                          ctx.author == ctx.guild.owner or \
                          ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m.id

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

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
    async def ban(self, ctx, member: MemberID, *, reason=None):
        try:
            await ctx.guild.ban(discord.Object(id=member), reason=reason)
            await ctx.message.add_reaction('hqcaramel:361532992499220492')
        except:
            await ctx.message.add_reaction('tsumikuBlank:364178887917436933')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member: MemberID, *, reason=None):
        try:
            await ctx.guild.ban(discord.Object(id=member), reason=reason)
            await ctx.guild.unban(discord.Object(id=member), reason=reason)
            await ctx.message.add_reaction('hqcaramel:361532992499220492')
        except:
            await ctx.message.add_reaction('tsumikuBlank:364178887917436933')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason=None):
        try:
            await ctx.guild.unban(member.user, reason=reason)
            await ctx.message.add_reaction('hqcaramel:361532992499220492')
        except Exception as e:
            await ctx.send(e)
            await ctx.message.add_reaction('tsumikuBlank:364178887917436933')

def setup(bot):
    bot.add_cog(Moderation(bot))
