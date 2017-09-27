import datetime
import sys
import traceback

import discord
from discord.ext import commands

import config
from cogs.utils.helpformatter import RubHelpFormatter

desc = 'A bot for rubs'

cogs = [
    'cogs.Admin',
    'cogs.Memes'
]

class Rub(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=['!', '`', '.'], description=desc, pm_help=None, help_attrs=dict(hidden=True),
                         formatter=RubHelpFormatter())
        self.load_cogs()
        self.add_command(self.source)

    def load_cogs(self):
        for cog in cogs:
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

    async def on_command_error(self, ctx, error):
        # TODO: Add extra error handling
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send('Sorry. This command is disabled and cannot be used.')
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
        await ctx.send('no')


if __name__ == '__main__':
    rub = Rub()
    rub.run()