import asyncio
from discord.ext import commands

import discord


class Helpful:
    """Random helpful commands"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        """Show someones avatar."""
        if not user:
            user = ctx.author
        await ctx.send(embed=discord.Embed().set_image(url=user.avatar_url).set_footer(text=str(user)))

    @commands.has_permissions(manage_messages=True)
    @commands.group()
    async def clear(self, ctx):
        if not ctx.invoked_subcommand:
            return False

    @commands.has_permissions(manage_messages=True)
    @clear.command()
    async def all(self, ctx, amount: int = 50):
        messages = await ctx.channel.history(limit=amount).flatten()
        await ctx.channel.delete_messages(messages)

    @commands.has_permissions(manage_messages=True)
    @clear.command()
    async def nonbot(self, ctx, amount: int = 50):
        messages = await ctx.channel.history(limit=amount).filter(lambda m: not m.author.bot).flatten()
        await ctx.channel.delete_messages(messages)

    @commands.has_permissions(manage_messages=True)
    @clear.command()
    async def images(self, ctx, amount: int = 50):
        def no_image(message):
            if message.embeds:
                data = message.embeds[0]
                if data.type == 'image':
                    return False
                if data.type == 'rich':
                    return False

            if message.attachments:
                return False
            return True

        messages = await ctx.channel.history(limit=amount).filter(no_image).flatten()
        out = ''
        for m in messages:
            out += f"{m.author}: {m.content.replace('`', '')[:40]}..\n"
        out = f'Delete? `y/n`:```\n{out[:1970]}\n```'
        bm = await ctx.send(out)
        def check(msg):
            if msg.author != ctx.author:
                return False
            if 'y' in msg.content.lower() or 'n' in msg.content.lower():
                return True
        try:
            r = await self.bot.wait_for('message', check=check, timeout=25)
            await bm.delete()
            if 'y' in r.content:
                messages += [r]
                await ctx.channel.delete_messages(messages)
                await (await ctx.send('Dun!')).edit(delete_after=5)
        except asyncio.TimeoutError:
            await bm.delete()
            await ctx.message.delete()



def setup(bot):
    bot.add_cog(Helpful(bot))
