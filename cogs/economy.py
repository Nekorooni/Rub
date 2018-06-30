import asyncio
import random
from enum import Enum

import itertools

import discord
from discord.ext import commands

from cogs.utils.cooldowns import basic_cooldown

base_colors = [
    ("Red", 424579184216506368, 30),
    ("Yellow", 424579315066208276, 30),
    ("Green", 424579385983762432, 30),
    ("Orange", 424579446578872332, 30),
    ("Cyan", 424579523363733507, 30),
    ("Blue", 424579641802752000, 30),
    ("Purple", 424579707573633024, 30),
    ("Pink", 424579770240466951, 30),
    ("Charcoal", 424579833994149888, 30),
]

extra_colors = [
    ("Cold Winter Breeze", 403584549847564304,45),
    ("Brilliant Bronze", 399125560661377025,45),
    ("Twilight", 360765369180225556,45),
    ("Journey", 360792645389516811,45),
    ("Love Is In The Air", 360765505788968961,60),
    ("The Light Of A Soul That Will Never Fade", 360792991968788480,60),
    ("Burning Passion", 360766053678055424,60),
    ("Seductive Embrace", 383816911072395269,60),
    ("A Story Untold", 360785400798904331,60),
    ("Reflections Of A Day Long Gone", 360791701025062913,60),
    ("A Darkness Only Seen Within", 360788545759084554,100),
    ("Spring Petal Dancing In The Mist", 403591076532846596,100),
    ("Lost in the Orchid Garden", 403583624558936065,100),
    ("Look Into The Stars", 369825912813780993,100),
    ("Walkin' on a Sunset", 383817936898490378,100),
]


class Shop:
    __slots__ = ('name', 'description', 'items')

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.items = []

    def add(self, item):
        self.items += [item]

    def get(self, item):
        return discord.utils.get(self.items, name=item)


class ItemType(Enum):
    GENERIC = 0
    ROLE = 1


class Item:
    __slots__ = ('name', 'type', 'cost', 'data')

    def __init__(self, name, type, cost, data):
        self.name = name
        self.type = type
        self.cost = cost
        self.data = data

    def get_role(self):
        return 0

    def __repr__(self):
        return f"<Item name='{self.name} type={self.type} cost={self.cost} data={self.data}>"


class Economy:

    def __init__(self, bot):
        self.bot = bot
        self.profiles = bot.get_cog("Profiles")
        self.shops = [
            Shop('Role shop', 'You can buy common colors here'),
            Shop('Premium shop', 'You can buy premium colors here')
        ]
        for name, data, cost in base_colors:
            self.shops[0].add(Item(name, ItemType.ROLE, cost=cost, data=data))
        for name, data, cost in extra_colors:
            self.shops[1].add(Item(name, ItemType.ROLE, cost=cost, data=data))

    @basic_cooldown(86400)
    @commands.guild_only()
    @commands.command(aliases=['daily'])
    async def dailies(self, ctx):
        """Claim your daily gold"""
        amount = random.randint(1, 5)
        async with self.profiles.get_lock(ctx.author.id):
            profile = await self.profiles.get_profile(ctx.author.id, ('coins',))
            profile.coins += amount
            await profile.save(self.bot.db)
        await ctx.send(f"You got {amount} gold as daily reward.")

    @dailies.error
    async def dailies_error(self, ctx, error):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)

        t = f"{h:.0f} hour(s)" if h else f"{m:.0f} minute(s) and {s:.0f} second(s)" if m else f"{s:.0f} second(s)"
        msg = "You already collected your dailies.\nTry again in " + t

        await ctx.send(msg)

    async def get_owned_colors(self, user_id):
        owned = itertools.chain(*await self.bot.db.fetch(f'SELECT color FROM colors WHERE user_id={user_id}'))
        return list(owned)

    @commands.guild_only()
    @commands.group(hidden=True, invoke_without_command=True)
    async def shop(self, ctx, *, name=None):
        """Check out the shop"""
        if ctx.invoked_subcommand is not None:
            return
        owned = await self.get_owned_colors(ctx.author.id)
        profile = await self.profiles.get_profile(ctx.author.id, ('coins',))

        em = discord.Embed(title="Color shop~", description="You can buy your colors here. To buy, type `~buy [color]`")
        for shop in self.shops:
            for item in shop.items:
                text = f"<@&{item.data}>\n"
                price = "Bought~" if item.data in owned else f"{item.cost}g"
                em.add_field(name=f'\u200b', value=text+price)
        em.set_footer(text=f"You have {profile.coins} gold")
        await ctx.send(embed=em)

    @shop.command(name="reload")
    async def shop_reload(self, ctx):
        pass

    @commands.guild_only()
    @commands.command(hidden=True)
    async def buy(self, ctx, *, item_name):
        """Buy an item from the shop"""
        item_name = item_name.lower()
        role = discord.utils.find(lambda x: item_name in x.name.lower(), ctx.guild.roles)

        if not role:
            return await ctx.send(f"{item_name} is not a valid role.")

        for shop in self.shops:
            item = discord.utils.find(lambda x: role.id == x.data, shop.items)
            if item:
                break
        else:
            return await ctx.send(f"{role.name} is not for sale.")

        owned = await self.get_owned_colors(ctx.author.id)

        # TODO: Handle non role items
        if item.data not in owned:
            async with self.profiles.get_lock(ctx.author.id):
                profile = await self.profiles.get_profile(ctx.author.id, ('coins',))
                if profile.coins >= item.cost:
                    profile.coins -= item.cost
                    await ctx.send(f"Thanks for buying <@&{item.data}>!")
                else:
                    return await ctx.send(f"You don't have enough gold for <@&{item.data}>")
                await profile.save(self.bot.db)
            await self.bot.db.execute(f'INSERT INTO colors (user_id, color) VALUES ({ctx.author.id}, {item.data})')
        else:
            await ctx.send(f"I'll swap your color to <@&{item.data}>")

        topcolor = self.profiles.get_top_color(ctx.author.roles)
        if topcolor:
            await ctx.author.remove_roles(topcolor)

        role = discord.utils.get(ctx.guild.roles, id=item.data)
        await ctx.author.add_roles(role)

    @commands.guild_only()
    @commands.command(aliases=['colors'])
    async def colours(self, ctx):
        """Display your owned colors"""
        owned = await self.get_owned_colors(ctx.author.id)
        if owned:
            await ctx.send("You own the following colors:\n"+'\n'.join([f"<@&{role}>" for role in owned]))
        else:
            await ctx.send("You don't own any colors at the moment.")

    def init_shop(self):
        self.shops = [
            Shop('Role shop', 'You can buy colours here')
        ]
        for name, data, cost in base_colors+extra_colors:
            self.shops[0].add(Item(name, ItemType.ROLE, cost=cost, data=data))

    @commands.guild_only()
    @commands.command(aliases=['wallet', 'gold', 'money', 'coins'])
    async def balance(self, ctx, *, member: discord.Member = None):
        """Check how much gold you have"""
        if member is None:
            member = ctx.author

        profile = await self.profiles.get_profile(member.id, ('coins',))

        await ctx.send(embed=discord.Embed(title=f"{member.display_name} has {profile.coins} gold"))

    @commands.guild_only()
    @commands.command(aliases=['sendmoney', 'pay', 'tip'])
    async def givemoney(self, ctx, receiver: discord.Member = None, amount: int = 0):
        """Send some gold to someone"""
        if receiver is None:
            return await ctx.send("I don't know who you want to give money to.")
        if amount <= 0:
            return await ctx.send('Please provide an amount above 0.')

        sender = await self.profiles.get_profile(ctx.author.id, ('coins',))

        if sender.coins < amount:
            return await ctx.send("You don't have enough gold to transfer that much.")

        await ctx.send(embed=discord.Embed(description=f"Are you sure you want to send {amount}g to {receiver}? `y / n`"))
        response = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id)

        if 'y' in response.content.lower():
            async with self.profiles.get_lock(ctx.author.id):
                sender = await self.profiles.get_profile(ctx.author.id, ('coins',))
                if sender.coins < amount:
                    return await ctx.send("You somehow don't have the funds to do this anymore.")
                sender.coins -= amount
                await sender.save(self.bot.db)
            async with self.profiles.get_lock(receiver.id):
                taker = await self.profiles.get_profile(receiver.id, ('coins',))
                taker.coins += amount
                await taker.save(self.bot.db)
            await ctx.send(embed=discord.Embed(description=f"You sent {receiver} {amount}g."))
        else:
            return await ctx.send("Transfer cancelled.")


def setup(bot):
    bot.add_cog(Economy(bot))
