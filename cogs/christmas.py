import asyncio
import datetime
import random

import discord
from discord.ext import commands

from cogs.profiles import needs_profile

ENTRIES_CHANNEL = 393157218343845888
LOTTO_COST = 100

class Christmas:

    def __init__(self, bot):
        self.bot = bot
        self.entries = []

    @commands.command()
    @commands.guild_only()
    @needs_profile(['coins'])
    async def lotto(self, ctx):
        """Enter the christmas event for only $5.99"""
        if ctx.author.id in self.entries:
            return await ctx.send('You already entered.')
        if ctx.profile.coins >= 100:
            ctx.profile.coins -= 100
            await ctx.profile.save(self.bot.db)
            self.entries += [ctx.author.id]
            await ctx.send('You bought a ticket for 100 coins')
            ch = ctx.guild.get_channel(ENTRIES_CHANNEL)
            await ch.send(f'{ctx.author.mention}: <{ctx.author.id}> entered')
        else:
            await ctx.send('You don\'t have 100 coins.')

    @commands.command()
    @commands.has_any_role('Admin')
    async def forcelotto(self, ctx, member:discord.Member):
        self.entries += [member.id]
        await ctx.send('dun')

    @commands.command()
    @commands.has_any_role('Admin')
    async def countdown(self, ctx, old_message=None):
        em = discord.Embed(title="Time till next draw", description="--:--:--")
        if old_message:
            msg = await ctx.channel.get_message(old_message)
        else:
            msg = await ctx.send(embed=em)

        today = datetime.datetime.utcnow()
        drawtime = datetime.datetime(year=today.year, month=today.month,
                            day=today.day, hour=22, minute=0, second=0)
        while datetime.datetime.utcnow() < drawtime:
            h, r = divmod(int((drawtime-datetime.datetime.utcnow()).total_seconds()), 60*60)
            m, s = divmod(r, 60)
            em.description = f'{h:02} hours : {m:02} minutes'
            await msg.edit(embed=em)
            await asyncio.sleep(60)

    @commands.command()
    @commands.has_any_role('Admin')
    async def droprolegift(self, ctx, channel: discord.TextChannel = None):
        ch = self.bot.get_channel(channel.id if channel else 370941450361372672)

        rewards = {
            'srare': [
                '<@&389521930794958858>',  # Dazzling Eve
                '<@&389485384058273795>',  # Christmas Lily
            ],
            'rare': [
                '<@&389481754253328405>',  # Snow Hallation
                '<@&389488875665358849>',  # Christmas Star
                '<@&389561947085078539>',  # Christmas night
            ],
            'common': [
                '<@&389516287170183198>',  # Cinnamon
                '<@&389109179257847808>',  # Snow spirit
                '<@&389519181407715329>',  # Christmas Berry
            ]
        }

        for i in range(10):
            emb = discord.Embed(color=discord.Color(0xfdd888))
            emb.add_field(name='<:presento:389142736420339714> A present magically appeared on the floor!',
                          value="Type `grab` to claim it!")
            gift = await ch.send(embed=emb)
            try:
                msg = await self.bot.wait_for('message', check=lambda
                    m: m.author != self.bot.user and m.channel.id == ch.id and 'grab' in m.content.lower(), timeout=180)
                emb = discord.Embed(color=discord.Color(0xfdd888))

                present = None
                r = random.randrange(0, 25)
                if r == 0:
                    present = 'A ultra rare role color: ' + random.choice(rewards['srare'])
                elif r < 9:
                    present = 'A rare role color: ' + random.choice(rewards['rare'])
                else:
                    present = 'A common role color: ' + random.choice(rewards['common'])
                emb.add_field(
                    name=f'<:presentoOpen:389142737175183371> {msg.author.name} opened up the present and found..',
                    value=present)
                await ch.send(embed=emb)
            except asyncio.TimeoutError:
                await ch.send('too slow', delete_after=2)
            finally:
                await gift.delete()
                t = random.randrange(300, 1200)
                print(f'Sleeping for {t} seconds')
                await asyncio.sleep(t)

    @commands.command()
    @commands.has_any_role('Admin')
    async def dropraingift(self, ctx, channel: discord.TextChannel = None):
        ch = self.bot.get_channel(channel.id if channel else 370941450361372672)
        emb = discord.Embed(color=discord.Color(0xfdd888))
        emb.add_field(name='<:presento:389142736420339714> A present magically appeared on the floor!',
                      value="Type `grab` to claim it!")
        gift = await ch.send(embed=emb)
        try:
            msg = await self.bot.wait_for('message', check=lambda
                m: m.author != self.bot.user and m.channel.id == ch.id and 'grab' in m.content.lower(), timeout=180)
            emb = discord.Embed(title=f'💥 {msg.author.name} opened up the present but it exploded.',
                                color=discord.Color(0xfdd888))
            await ch.send(embed=emb, delete_after=6)
        except asyncio.TimeoutError:
            await ch.send('too slow', delete_after=2)
        finally:
            await gift.delete()
            await asyncio.sleep(10)
        emb = discord.Embed(title=f'You hear something in the distance',
                            color=discord.Color(0xfdd888))
        await ch.send(embed=emb, delete_after=6)

    @commands.command()
    @commands.has_any_role('Admin')
    async def dropfakegift(self, ctx, channel: discord.TextChannel = None):
        ch = self.bot.get_channel(channel.id if channel else 370941450361372672)
        emb = discord.Embed(color=discord.Color(0xfdd888))
        emb.add_field(name='<:presento:389142736420339714> A present magically appeared on the floor!',
                      value="Type `grab` to claim it!")
        gift = await ch.send(embed=emb)
        try:
            msg = await self.bot.wait_for('message', check=lambda
                m: m.author != self.bot.user and m.channel.id == ch.id and 'grab' in m.content.lower(), timeout=180)
            emb = discord.Embed(title=f'💥 {msg.author.name} opened up the present but it exploded.',
                                color=discord.Color(0xfdd888))
            await ch.send(embed=emb, delete_after=6)
        except asyncio.TimeoutError:
            await ch.send('too slow', delete_after=2)
        finally:
            await gift.delete()

    @commands.command()
    @commands.has_any_role('Admin')
    async def fortunecookierain(self, ctx, channel: discord.TextChannel = None):
        ch = self.bot.get_channel(channel.id if channel else 370941450361372672)
        emb = discord.Embed(color=discord.Color(0xfdd888))
        emb.add_field(name='<:fortunecookie:390188838586155029> It\'s raining fortune cookies!',
                      value="Type `catch` to claim one!")
        gift = await ch.send(embed=emb)
        winners = {}
        try:
            for i in range(10):
                msg = await self.bot.wait_for('message', check=lambda
                    m: m.author != self.bot.user and m.channel.id == ch.id and 'catch' in m.content.lower() and m.author not in winners, timeout=10)
                num = random.randrange(1, 100)
                emb = discord.Embed(title=f'💥 {msg.author.name} caught the cookie and opened it..',
                                    description=f'The message said `{num}` nani',
                                    color=discord.Color(0xfdd888))
                winners[msg.author] = num
                await ch.send(embed=emb)
        except asyncio.TimeoutError:
            pass
        finally:
            await gift.delete()
            output = '```'+'\n'.join([f'{k.name} got number {v}' for k, v in winners.items()])+'```'
            await ch.send(output)


def setup(bot):
    bot.add_cog(Christmas(bot))
