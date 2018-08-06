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
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, *members: MemberID):
        permissions = ctx.channel.permissions_for(ctx.author)
        if getattr(permissions, 'ban_members', None):
            for member in members:
                try:
                    await ctx.guild.ban(discord.Object(id=member))
                    member = await self.bot.get_user_info(member)
                    await ctx.send(f'Banned {member}!')
                except Exception as e:
                    await ctx.send(e)
        else:
            ch = self.bot.get_channel(STAFF_CHANNEL)
            await ch.send(f"<@&293008190843387911> {ctx.author.mention} requests mass banning {' '.join(members)}.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def block(self, ctx, member: discord.Member, minutes: int = 5):
        await member.add_roles(discord.utils.get(ctx.guild.roles, name='Block desu'),
                               reason=f"Blocked for {minutes} minutes")
        await self.timers.create_timer('unblock', datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
                                       [ctx.guild.id, member.id])
        await ctx.message.add_reaction('hqcaramel:361532992499220492')

    async def on_unblock_event(self, guild_id, user_id):
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        await member.remove_roles(discord.utils.get(guild.roles, name='Block desu'))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int = 5):
        await member.add_roles(discord.utils.get(ctx.guild.roles, name='Mute'),
                               reason=f"Muted for {minutes} minutes")
        await self.timers.create_timer('unmute', datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
                                       [ctx.guild.id, member.id])
        await ctx.message.add_reaction('hqcaramel:361532992499220492')

    async def on_unmute_event(self, guild_id, user_id):
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        await member.remove_roles(discord.utils.get(guild.roles, name='Mute'))

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
            await ctx.send(f'Bump reminder set for {t} (UTC) <a:anzu2:393962410119135232>')
        else:
            await ctx.send(f'Please supply a better time format.')

    async def on_bumpreminder_event(self):
        ch = self.bot.get_channel(462824492247285762)
        e = discord.Embed(title="Server can be bumper", colour=discord.Colour.purple(),
                          description=f'Click [here](https://discord.me/server/bump-servers/48294) for the bump page!')
        e.timestamp = datetime.datetime.utcnow()
        await ch.send(embed=e)

    @commands.group(invoke_without_command=True, aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Clear messages in a channel"""
        amount = min(amount, 50)
        messages = await ctx.channel.history(limit=amount+1).flatten()
        await ctx.channel.delete_messages(messages)
        await ctx.send(f'Deleted {len(messages)} messages', delete_after=4)

    @clear.command(name="member", aliases=['user'])
    @commands.has_permissions(manage_messages=True)
    async def clear_member(self, ctx, member: discord.Member, amount: int = 10):
        """Clear messages from a specific user"""
        messages = await ctx.channel.history(limit=amount+1).filter(lambda m: m.author.id==member.id).flatten()

        await ctx.channel.delete_messages(messages)
        await ctx.send(f'Deleted {len(messages)} messages', delete_after=4)

    @clear.command(name="nonimage", aliases=['text'])
    @commands.has_permissions(manage_messages=True)
    async def clear_nonimage(self, ctx, amount: int = 10):
        """Clear messages without attachments"""
        def check(message):
            if message.embeds:
                data = message.embeds[0]
                if data.type == 'image':
                    return False
                if data.type == 'rich':
                    return False

            if message.attachments:
                return False
            return True

        messages = await ctx.channel.history(limit=amount+1).filter(check).flatten()

        await ctx.channel.delete_messages(messages)
        await ctx.send(f'Deleted {len(messages)} messages', delete_after=4)

    @clear.command(name="bot")
    @commands.has_permissions(manage_messages=True)
    async def clear_bot(self, ctx, amount: int = 10):
        """Clear bot messages"""
        messages = await ctx.channel.history(limit=amount+1).filter(lambda m: m.author.bot).flatten()

        await ctx.channel.delete_messages(messages)
        await ctx.send(f'Deleted {len(messages)} messages', delete_after=4)

def setup(bot):
    bot.add_cog(Moderation(bot))
