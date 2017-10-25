import aiohttp
from discord.ext import commands

import discord
import random

from cogs.profiles import needs_profile


def has_item(**kwargs):
    async def predicate(ctx):
        if ctx.guild is None:
            return False
        kwargs['profile_id'] = ctx.profile.pid
        items = await ctx.bot.db.fetch(f'SELECT * FROM `inventory` '
                                       f'WHERE '+' AND '.join([f'{k}="{v}"' for k, v in kwargs.items()]))

        return len(items) > 0
    return commands.check(predicate)


class Inventory:
    """Inventory stuff"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['inv'])
    @needs_profile()
    async def inventory(self, ctx):
        items = await ctx.bot.db.fetch(f'SELECT it.name, it.shortdesc, data FROM inventory '
                                       f'INNER JOIN items it ON item_id=it.id WHERE profile_id={ctx.profile.pid}')
        if items:
            await ctx.send('\n'.join([f'{name}{" "+data if data else ""} - {short}' for name, short, data in items]))
        else:
            await ctx.send("You don't have anything.")

    @commands.command()
    @needs_profile()
    @has_item(id=1)
    async def use(self, ctx):
        await ctx.send('All gud!')

def setup(bot):
    bot.add_cog(Inventory(bot))
