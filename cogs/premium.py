import discord
from discord.ext import commands
from cogs.inventory import needs_profile

def get_color_role(member):
    for role in member.roles:
        if role.color == member.color:
            return role

class Premium:
    """Premium stuff for premium people"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @needs_profile()
    async def color(self, ctx, color: discord.Role):
        c = get_color_role(ctx.author)
        if await ctx.bot.db.fetchone(f'SELECT id FROM inventory '
                                     f'WHERE profile_id="{ctx.profile.pid}" '
                                     f'AND item_id="10" AND data="{color.name}"'):
            await ctx.author.add_roles(color)
            await ctx.author.remove_roles(c)
            await ctx.send("There you go!")
        else:
            await ctx.send("You don't have that coupon.")

def setup(bot):
    bot.add_cog(Premium(bot))
