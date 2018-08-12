import datetime
import sys
import os
import traceback

import discord
from discord.ext import commands
import aiohttp
import aioredis

import config
from cogs.utils import context, db
from cogs.utils.helpformatter import RubHelpFormatter

desc = 'A bot for rubs'

async def get_pre(bot, message):
    if message.guild and message.guild.id not in bot.prefixes:
        bot.prefixes[message.guild.id] = await bot.redis.lrange(f'prefix:{message.guild.id}',0 , -1, encoding='utf8')
    return config.prefix + bot.prefixes[message.guild.id]

class Rub(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=get_pre, description=desc, pm_help=None, help_attrs=dict(hidden=True),
                         formatter=RubHelpFormatter(), case_insensitive=True)
        self.load_cogs()
        self.add_command(self.source)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.db = db.DB(config.db_host, config.db_user, config.db_pass, config.db_name, self.loop)
        self.redis = self.loop.run_until_complete(aioredis.create_redis_pool('redis://redis', loop=self.loop))
        self.redis = aioredis.Redis(self.redis)
        self.prefixes = {}

    def load_cogs(self):
        for cog in os.getenv('BASE_COGS').split():
            try:
                self.load_extension(cog)
            except Exception as e:
                print(f"Cog '{cog}' failed to load.", file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(f'Ready: {self.user} (ID: {self.user.id})')
        print(f'Discord {discord.__version__}')

    async def on_resumed(self):
        print('Resumed..')

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)

        if ctx.command is None:
            return

        await self.invoke(ctx)

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        # TODO: Add extra error handling
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command is only for use inside guilds.')
        elif isinstance(error, commands.DisabledCommand):
            pass
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("Please wait before using this command again.")
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)

    @property
    def config(self):
        return __import__('config')

    def run(self):
        super().run(config.token)

    @commands.command()
    async def source(self, ctx):
        """A link to Rub's source code"""
        await ctx.send('https://github.com/Nekorooni/Rub')


if __name__ == '__main__':
    rub = Rub()
    rub.run()
