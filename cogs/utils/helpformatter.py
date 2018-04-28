import asyncio
import inspect

import itertools
from discord.ext.commands import HelpFormatter, Paginator, Command


def signature(cmd):
    """Returns a POSIX-like signature useful for help command output."""
    result = []
    parent = cmd.full_parent_name

    name = cmd.name if not parent else parent + ' ' + cmd.name
    result.append(name)

    if cmd.usage:
        result.append(cmd.usage)
        return ' '.join(result)

    params = cmd.clean_params
    if not params:
        return ' '.join(result)

    for name, param in params.items():
        if param.default is not param.empty:
            # We don't want None or '' to trigger the [name=value] case and instead it should
            # do [name] since [name=None] or [name=] are not exactly useful for the user.
            should_print = param.default if isinstance(param.default, str) else param.default is not None
            if should_print:
                result.append('[%s=%s]' % (name, param.default))
            else:
                result.append('[%s]' % name)
        elif param.kind == param.VAR_POSITIONAL:
            result.append('[%s...]' % name)
        else:
            result.append('<%s>' % name)

    add = "\n\nAliases:\n"+', '.join(f'  {alias}' for alias in cmd.aliases) if len(cmd.aliases) > 0 else ''

    return ' '.join(result)+add

class RubHelpFormatter(HelpFormatter):

    def __init__(self):
        super().__init__()

    def get_ending_note(self):
        return ''

    @asyncio.coroutine
    def format(self):
        """Handles the actual behaviour involved with formatting.

        To change the behaviour, this method should be overridden.

        Returns
        --------
        list
            A paginated output of the help command.
        """
        self._paginator = Paginator(prefix='```md')

        # we need a padding of ~80 or so

        description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

        if description:
            # <description> portion
            self._paginator.add_line(f'[ {description} ][-!`.]', empty=True)

        if isinstance(self.command, Command):
            # <long doc> section
            if self.command.help:
                self._paginator.add_line(self.command.help, empty=True)

            # <signature portion>
            signature = self.get_command_signature()
            self._paginator.add_line(f"Usage:")
            self._paginator.add_line(f"{signature}", empty=True)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close_page()
                return self._paginator.pages

        max_width = self.max_name_size

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return f' <{cog}>' if cog is not None else '<Other>'

        filtered = yield from self.filter_command_list()
        if self.is_bot():
            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                commands = sorted(commands)
                if len(commands) > 0:
                    self._paginator.add_line(category)

                self._add_subcommands_to_page(max_width, commands)
        else:
            filtered = sorted(filtered)
            if filtered:
                self._paginator.add_line('<Commands>')
                self._add_subcommands_to_page(max_width, filtered)

        # add the ending note
        self._paginator.add_line()
        ending_note = self.get_ending_note()
        self._paginator.add_line(ending_note)
        return self._paginator.pages

    def get_command_signature(self):
        """Retrieves the signature portion of the help page."""
        prefix = self.clean_prefix
        cmd = self.command
        return prefix + signature(cmd)


    def _add_subcommands_to_page(self, max_width, commands):
        for name, command in commands:
            if name in command.aliases:
                # skip aliases
                continue

            entry = ' {0:>{width}} : {1}'.format(name, command.short_doc, width=max_width)
            shortened = self.shorten(entry)
            self._paginator.add_line(shortened)
