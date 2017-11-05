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
        await ctx.send(user.avatar_url)

    @commands.group()
    async def cleanup(self, ctx):
        if not ctx.invoked_subcomand:
            return False

    @cleanup.command()
    async def images(self, ctx, amount: int = 10):
        out = ''

        def pred(message):
            if message.embeds:
                data = message.embeds[0]
                if data.type == 'image':
                    return False

            if message.attachments:
                return False
            return True

        messages = await ctx.channel.history(limit=amount).filter(pred).flatten()

        for m in messages:
            out += f"{m.author}: {m.content.replace('`', '')}\n"
        out = f'Delete? `y/n`:```\n{out[:1970]}\n```'
        bm = await ctx.send(out)
        r = await self.bot.wait_for('message', check=lambda m: 'y' in m.content.lower() or 'n' in m.content.lower())
        if 'y' in r.content:
            await ctx.channel.delete_messages(messages)
            await (await ctx.send('Dun!')).edit(delete_after=3)
        await ctx.delete(bm)


def setup(bot):
    bot.add_cog(Helpful(bot))
