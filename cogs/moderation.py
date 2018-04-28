from discord.ext import commands
from .utils import time
import asyncio
import discord
import parsedatetime as pdt
import datetime

def get_date(text):
    cal = pdt.Calendar()
    time, res = cal.parseDT(text, datetime.datetime.utcnow())
    return time if res else None

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
        self.timers = bot.get_cog('Timers')

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

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def block(self, ctx, member: discord.Member, minutes: int=5):
        await member.add_roles(discord.utils.get(ctx.guild.roles, name='Block desu'))
        await self.timers.create_timer('unblock', datetime.datetime.utcnow()+datetime.timedelta(minutes=minutes),
                                       [ctx.guild.id, member.id])

    async def on_unblock_event(self, guild_id, user_id):
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        await member.remove_roles(discord.utils.get(guild.roles, name='Block desu'))

    async def on_unmute_event(self, user_id):
        pass

    @commands.command(aliases=['finduser'])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def userfind(self, ctx, *, search):
        found = []
        for m in ctx.guild.members:
            if search.lower() in m.name.lower():
                found+=[m]
        if found:
            await ctx.send('Matches users:```\n'+'\n'.join([f'{m} ({m.id})' for m in found])+'```')
        else:
            await ctx.send('Found nothing')

    @commands.command(aliases=['newmembers'])
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def newusers(self, ctx, *, count=5):
        """Tells you the newest members of the server.
        This is useful to check if any suspicious members have
        joined.
        The count parameter can only be up to 25.
        """
        count = max(min(count, 25), 5)

        if not ctx.guild.chunked:
            await self.bot.request_offline_members(ctx.guild)

        members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:count]

        e = discord.Embed(title='New Members', colour=discord.Colour.green())

        for member in members:
            body = f'joined {time.time_ago(member.joined_at)}, created {time.time_ago(member.created_at)}'
            e.add_field(name=f'{member} (ID: {member.id})', value=body, inline=False)

        await ctx.send(embed=e)

    @commands.command(aliases=['infouser'])
    @commands.guild_only()
    async def userinfo(self, ctx, *, member: discord.Member):
        e = discord.Embed(title=f'{member} (ID: {member.id})', colour=discord.Colour.green())
        e.set_thumbnail(url=member.avatar_url_as(size=128))
        e.add_field(name=f'Joined', value=time.time_ago(member.joined_at), inline=True)
        e.add_field(name=f'Created', value=time.time_ago(member.created_at), inline=True)
        e.add_field(name=f'Nickname', value=member.nick or "None", inline=False)
        e.add_field(name=f'Roles', value=' '.join([role.mention for role in member.roles[1:]]) or "None", inline=False)
        await ctx.send(embed=e)

    @commands.command(aliases=['bumped'])
    @commands.has_role('Staff')
    async def bump(self, ctx, *, time_till_bump='6h'):
        """Tell Rub you bumped the server so she can remind you.
        Defaults to 6 hours if you leave the time out.

        You can copy the exact time as shown on discord.me as time input, for example:
        !bump 4h 21m 54s
        """
        t = get_date(time_till_bump)
        if t:
            await self.timers.create_timer('bumpreminder', t)
            await ctx.send(f'Bump reminder set for {t} (UTC) <a:twitch:406319471272263681>')
        else:
            await ctx.send(f'Please supply a better time format.')

    async def on_bumpreminder_event(self):
        ch = self.bot.get_channel(370941450361372672)
        e = discord.Embed(title="Server can be bumper", colour=discord.Colour.purple(),
                          description=f'Click [here](https://discord.me/server/bump-server/48294) for the bump page!')
        e.timestamp = datetime.datetime.utcnow()
        await ch.send(embed=e)

def setup(bot):
    bot.add_cog(Moderation(bot))
