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
            await self.log('edit', before.author.id, before.channel.id, before.content)

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

        def callback(page):
            em = discord.Embed(title=f'Recent deletions from {member}')
            for c, a in rows[page*5:page*5+5]:
                em.add_field(name=member.display_name, value=c or '-', inline=False)
            em.set_footer(text=f'Page {page+1}')
            return em

        await self.embed_paginator(ctx, callback)

    @deletes.command(name='in')
    async def deletes_in(self, ctx, channel: discord.TextChannel):
        qry = f'SELECT user_id, content, attachments FROM monitorlog WHERE type="delete" AND channel={channel.id} ' \
              f'ORDER BY id DESC'
        rows = await self.bot.db.fetch(qry)

        if not rows:
            return await ctx.send('No deletes found')

        def callback(page):
            em = discord.Embed(title=f'Recent deletions in {channel}')
            for u, c, a in rows[page*5:page*5+5]:
                member = ctx.bot.get_user(u)
                em.add_field(name=member.display_name if member else 'unknown', value=c or '-', inline=False)
            em.set_footer(text=f'Page {page+1}')
            return em

        await self.embed_paginator(ctx, callback)


    async def embed_paginator(self, ctx, callback):
        buttons = ['◀', '▶', '⏹']
        index = 0

        msg = await ctx.send(embed=callback(index))
        for button in buttons:
            await msg.add_reaction(button)

        while True:
            try:
                def check(r, u):
                    return u.id == ctx.author.id and str(r) in buttons
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=120)
            except asyncio.TimeoutError:
                break
            else:
                await msg.remove_reaction(reaction, user)
                t = buttons.index(str(reaction))
                if t == 0:
                    if index > 0:
                        index -= 1
                        await msg.edit(embed=callback(index))
                elif t == 1:
                    index += 1
                    await msg.edit(embed=callback(index))
                else:
                    break
        await msg.delete()


def setup(bot):
    bot.add_cog(Monitor(bot))
