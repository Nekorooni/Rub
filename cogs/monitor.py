import asyncio
import discord
from contextlib import contextmanager
from discord.ext import commands

class Monitor:
    """Monitoring the world"""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    async def log(self, logtype, user_id, channel, content, attachments=''):
        await self.bot.db.execute(f'INSERT INTO `monitorlog` (`type`, `user_id`, `channel`, `content`, `attachments`) '
                                  f'VALUES (%s, %s, %s, %s, %s)', (logtype, user_id, channel, content, attachments))

    async def on_message_delete(self, message):
        att = '\n'.join(x.url for x in message.attachments)
        await self.log('delete', message.author.id, message.channel.id, message.content, att)

    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.log('edit', after.author.id, after.channel.id, after.content)

    async def on_command(self, ctx):
        await self.log('command', ctx.author.id, ctx.channel.id, ctx.message.content)

    # @commands.command()
    # async def deletes(self, ctx, target: DeleteTarget = None):
    #     if not target:
    #         target = ctx.channel.id
    #     deletes = await self.bot.db.fetch(
    #         'SELECT author, content FROM `monitorlog` WHERE type="delete" AND (`author`=%s OR `channel`=%s)',
    #         (target, target))
    #     await ctx.send('```\n' + '\n'.join(
    #         [f'{self.bot.get_user(author) or "?"} :{content}' for author, content in deletes]) + '```')

    @commands.group(invoke_without_command=True)
    async def deletes(self, ctx):
        if ctx.invoked_subcommand:
            return
        await ctx.send('deletes')

    @deletes.command(name='from')
    async def deletes_from(self, ctx, member: discord.Member):
        qry = f'SELECT content, attachments FROM monitorlog WHERE type="delete" AND user_id={member.id} ' \
              f'ORDER BY id DESC'
        rows = await self.bot.db.fetch(qry)

        if not rows:
            return await ctx.send('No deletes found')

        buttons = ['◀', '▶', '⏹']

        def gen_embed(page):
            em = discord.Embed(title=f'Recent deletions from {member}')
            for c, a in rows[page*5:page*5+5]:
                em.add_field(name=member.display_name, value=c or '-', inline=False)
            em.set_footer(text=f'Page {page+1}')
            return em

        index = 0

        msg = await ctx.send(embed=gen_embed(index))
        for button in buttons:
            await msg.add_reaction(button)

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id and str(r) in buttons)
            except asyncio.TimeoutError:
                break
            else:
                await msg.remove_reaction(reaction, user)
                t = buttons.index(str(reaction))
                if t == 0:
                    if index > 0:
                        index -= 1
                        await msg.edit(embed=gen_embed(index))
                elif t == 1:
                    index += 1
                    await msg.edit(embed=gen_embed(index))
                else:
                    break
        await msg.delete()

    @deletes.command(name='in')
    async def deletes_in(self, ctx, channel: discord.TextChannel):
        await ctx.send(channel)


def setup(bot):
    bot.add_cog(Monitor(bot))
