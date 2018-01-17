import aiohttp
from discord.ext import commands


class CleverWrap:

    url = "https://www.cleverbot.com/getreply"

    def __init__(self, api_key, name="Name"):
        self.name = name
        self.key = api_key
        self.history = {}
        self.convo_id = ""
        self.cs = ""
        self.count = 0
        self.time_elapsed = 0
        self.time_taken = 0
        self.output = ""

    async def say(self, text):
        params = {
            "input": text,
            "key": self.key,
            "cs": self.cs,
            "conversation_id": self.convo_id,
            "wrapper": "CleverWrap.py"
        }

        reply = await self._send(params)
        self._process_reply(reply)
        return self.output

    async def _send(self, params):
        # Get a response
        async with aiohttp.ClientSession() as sess:
            async with sess.get(self.url, params=params) as resp:
                if resp.status == 200:
                    res = await resp.json()
                    # print(res)
                    return res

    def _process_reply(self, reply):
        self.cs = reply.get("cs", None)
        self.count = reply.get("interaction_count", None)
        self.output = reply.get("output", None)
        self.convo_id = reply.get("conversation_id", None)
        self.history = {key: value for key, value in reply.items() if key.startswith("interaction")}
        self.time_taken = reply.get("time_taken", None)
        self.time_elapsed = reply.get("time_elapsed", None)

    def reset(self):
        self.cs = ""
        self.convo_id = ""


class Cleverbot:
    """Cleverbot stuff"""

    def __init__(self, bot):
        self.bot = bot
        self.sessions = dict()

    async def on_message(self, msg):
        if msg.author == self.bot.user:
            return
        if msg.channel.id == 362669211966767104 or msg.content.startswith('rubbu '):
            if msg.mentions:
                return
            if msg.content.startswith('.'):
                return
            if msg.author.id not in self.sessions:
                self.sessions[msg.author.id] = CleverWrap(self.bot.config.cleverbot_token, name=msg.author.name)
            async with msg.channel.typing():
                if msg.content:
                    await msg.channel.send(await self.sessions[msg.author.id].say(msg.content))
                elif msg.attachments:
                    await msg.channel.send(await self.sessions[msg.author.id].say(msg.attachments[0].filename.split('.')[0]))

    @commands.group()
    async def cleverbot(self, ctx):
        pass

    @cleverbot.command()
    async def reset(self, ctx):
        self.sessions[ctx.message.author.id].reset()
        await ctx.send("reset!")

    @cleverbot.command()
    async def transcript(self, ctx):
        await ctx.send("Not implemented :v")


def setup(bot):
    bot.add_cog(Cleverbot(bot))
