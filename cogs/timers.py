import asyncio
import json

import discord
from discord.ext import commands
import datetime


class Timer:
    __slots__ = ('id', 'event', 'expires', 'data')

    def __init__(self, *, record):
        self.id = record['id']

        self.event = record['event']
        self.expires = record['expires']
        self.data = json.loads(record['data'])

    @classmethod
    def temporary(cls, *, event, expires, data):
        pseudo = {
            'id': None,
            'event': event,
            'expires': expires,
            'data': ['no']
        }
        return cls(record=pseudo)

    def __repr__(self):
        return f'<Timer expires={self.expires} event={self.event}>'

class Timers:
    """Setting timers"""
    def __init__(self, bot):
        self.bot = bot
        self._current_timer = None
        self._task = bot.loop.create_task(self.remind_check_loop())

    async def remind_check_loop(self):
        await self.bot.wait_until_ready()
        try:
            while not self.bot.is_closed():
                qry = f'SELECT id, event, expires, data ' \
                      f'FROM timers ' \
                      f'WHERE expires < ("{datetime.datetime.utcnow()+datetime.timedelta(days=7)}") ' \
                      f'ORDER BY expires LIMIT 1'
                timer = await self.bot.db.fetchdict(qry)
                print(timer)
                if not timer:
                    self._current_timer = None
                    return await asyncio.sleep(3600)

                timer = self._current_timer = Timer(record=timer)
                now = datetime.datetime.utcnow()
                delta = timer.expires-now
                print(delta)
                if timer.expires > now:
                    await asyncio.sleep(delta.total_seconds())

                await self.finish_timer(timer)
        except asyncio.CancelledError:
            pass
        except (OSError, discord.ConnectionClosed, asyncio.TimeoutError):
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.remind_check_loop())
        except Exception as e:
            print(e)

    async def create_timer(self, event, expires, data=None):
        if data:
            data = json.dumps(data)
        else:
            data = []
        await self.bot.db.execute(f"INSERT INTO timers (event, expires, data) "
                                  f"VALUES ('{event}', '{expires}', '{data}')")

        if self._current_timer is None or self._current_timer and expires < self._current_timer.expires:
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.remind_check_loop())

    async def finish_timer(self, timer):
        self.bot.dispatch(f'{timer.event}_event', *timer.data)
        await self.bot.db.execute(f'DELETE FROM timers WHERE id={timer.id}')
        print(f'timer finished and deleted')

    @commands.command()
    async def testreminder(self, ctx, seconds: int, *, message):
        due = datetime.datetime.utcnow()+datetime.timedelta(seconds=seconds)
        await self.create_timer('reminder', due, [ctx.channel.id, message])

    async def on_testevent_timer_complete(self, channel_id, msg):
        ch = self.bot.get_channel(channel_id)
        await ch.send(msg)



    async def on_delayed_delete_timer_complete(self, channel_id, message_id):
        try:
            m = await self.bot.get_channel(channel_id).get_message(message_id)
            await m.delete()
        except:
            pass

def setup(bot):
    bot.add_cog(Timers(bot))
