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

    @commands.command()
    @commands.has_role('Admin')
    async def spawnitem(self, ctx, member:discord.Member, *, item_name):
        r,i = await ctx.bot.db.execute(f'INSERT INTO inventory (profile_id, item_id) '
                                       f'SELECT p.id, i.id '
                                       f'FROM profiles p '
                                       f'INNER JOIN items i '
                                       f'WHERE p.user_id={member.id} '
                                       f'AND i.name="{item_name}"')
        if r:
            await ctx.send('Dun!')
        else:
            await ctx.send('Something bad happened')



    @commands.command()
    @needs_profile()
    @has_item(id=1)
    async def use(self, ctx):
        await ctx.send('All gud!')

def setup(bot):
    bot.add_cog(Inventory(bot))
