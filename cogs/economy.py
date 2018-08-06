import asyncio
import random

import itertools

import discord
from discord.ext import commands

from cogs.utils.cooldowns import basic_cooldown

base_colors = [
    ("Kiwi", 390775426965831683, 150),
    ("Champagne", 396418315557535747, 150),
    ("Pistachio", 390785402640007169, 150),
    ("Cirno", 396075783803633674, 200),
    ("Shiina", 396051268583424013, 200),
    ("Maple", 390785965519798273, 300),
]

class Economy:

    def __init__(self, bot):
        self.bot = bot
        self.profiles = bot.get_cog("Profiles")

    async def give_coins(self, user_id, amount):
        await self.bot.redis.hincrby(f'user:{user_id}', 'coins', amount)

    async def get_coins(self, user_id):
        amount = await self.bot.redis.hget(f'user:{user_id}', 'coins') or 0
        return int(amount)

    @basic_cooldown(86400)
    @commands.guild_only()
    @commands.command(aliases=['daily'])
    async def dailies(self, ctx):
        """Claim your daily gold"""
        amount = random.randint(100, 150)
        await self.give_coins(ctx.author.id, amount)
        await ctx.send(f"You got {amount} gold as daily reward.")

    @dailies.error
    async def dailies_error(self, ctx, error):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)

        t = f"{h:.0f} hour(s)" if h else f"{m:.0f} minute(s) and {s:.0f} second(s)" if m else f"{s:.0f} second(s)"
        msg = "You already collected your dailies.\nTry again in " + t

        await ctx.send(msg)

    @commands.guild_only()
    @commands.command(aliases=['wallet', 'coins'])
    async def balance(self, ctx, *, member: discord.Member = None):
        """Check how much gold you have"""
        if member is None:
            member = ctx.author

        amount = await self.bot.redis.hget(f'user:{member.id}', 'coins') or 0

        await ctx.send(embed=discord.Embed(title=f"{member.display_name} has {int(amount)} coins"))

    @commands.guild_only()
    @commands.command(aliases=['pay', 'tip', 'sendcoins'])
    async def givecoins(self, ctx, receiver: discord.Member = None, amount: int = 0):
        """Give someone else your money"""
        if receiver is None:
            return await ctx.send("I don't know who you want to give money to.")
        if amount <= 0:
            return await ctx.send('Please provide an amount above 0.')

        if await self.get_coins(ctx.author.id) < amount:
            return await ctx.send("You don't have enough coins to transfer that much.")

        await ctx.send(embed=discord.Embed(description=f"Are you sure you want to send {amount}g to {receiver}? `y / n`"))
        response = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id)

        if 'y' in response.content.lower():
            async with self.profiles.get_lock(ctx.author.id):
                if await self.get_coins(ctx.author.id) < amount:
                    return await ctx.send("You somehow don't have the funds to do this anymore.")
                await self.give_coins(ctx.author.id, -amount)
                await self.give_coins(receiver.id, amount)
            await ctx.send(embed=discord.Embed(description=f"You sent {receiver} {amount}g."))
        else:
            return await ctx.send("Transfer cancelled.")


def setup(bot):
    bot.add_cog(Economy(bot))
