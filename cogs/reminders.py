import asyncio

import parsedatetime as pdt
from discord.ext import commands


def get_date(text):
    cal = pdt.Calendar()
    time, res = cal.parseDT(text)
    return time if res else None

class Reminders:
    """Tools for reminding me"""
    def __init__(self, bot):
        self.bot = bot
        self.reminders = []
        self.bot.loop.create_task(self.remind_check_loop())

    async def on_message(self, msg):
        if msg.content.lower().startswith('remind '):
            reminder = msg.content[7:]
            if reminder.lower().startswith('me '):
                reminder = reminder[3:]
            if reminder.lower().startswith('to '):
                reminder = reminder[3:]

            time = get_date(reminder)
            if not time:
                await msg.channel.send("When?")
                msg = await self.bot.wait_for('message',
                                              check=lambda m: m.author == msg.author and m.channel == msg.channel)
                time = get_date(msg.content)
            if time:
                if await self.make_reminder(msg.author.id, reminder, time):
                    await msg.channel.send(f"I'll remind you at {time}")
                else:
                    await msg.channel.send(f"There was a problem setting your reminder.")
            else:
                await msg.channel.send(f"Idk when you want me to remind you")

    async def make_reminder(self, author_id, note, due):
        try:
            await self.bot.db.execute(f'INSERT INTO reminders (author, note, due) VALUES ({author_id}, "{note}", "{due}")')
            return True
        except Exception as e:
            print(e)
            return False

    async def remind_check_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(60)
            reminders = await self.bot.db.fetch('SELECT id, author, note FROM reminders WHERE NOT done AND due<NOW()')
            for _id, author, note in reminders:
                await self.bot.db.execute(f'UPDATE reminders SET done=1 WHERE id={_id}')
                await self.bot.get_user(author).send(f"**I had to remind you:**\n{note} <:blobcaramel:325504959544295424>")

def setup(bot):
    bot.add_cog(Reminders(bot))
