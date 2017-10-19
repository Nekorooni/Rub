from discord.ext import commands
import discord


CARAMEL_CHANNEL = 369821496010604554
CARAMEL_THRESHOLD = 3


class Caramelboard:
    """Stuff for the caramelboard"""

    async def on_raw_reaction_add(self, emoji, message_id, channel_id, user_id):
        if 'caramel' not in emoji.name:
            return
        if channel_id == CARAMEL_CHANNEL:
            return

        channel = self.bot.get_channel(channel_id)
        msg = await channel.get_message(message_id)
        if await self.count_caramels(msg) < CARAMEL_THRESHOLD:
            return

        r = await self.bot.db.fetchone(f'SELECT * FROM `caramelboard` WHERE message_id={message_id}')
        if r:
            pass
        else:
            emb = self.make_embed(msg)
            post = await self.bot.get_channel(CARAMEL_CHANNEL).send(embed=emb)
            await self.bot.db.execute(
                f'INSERT INTO `caramelboard` (message_id, bot_message_id) VALUES ({message_id}, {post.id})')

    async def on_raw_reaction_remove(self, emoji, message_id, channel_id, user_id):
        pass

    def make_embed(self, msg):
        emb = discord.Embed(description=msg.content)
        emb.set_author(name=msg.author.name, icon_url=msg.author.avatar_url_as(size=64))
        if msg.attachments:
            emb.set_image(url=msg.attachments[0].url)
        elif msg.embeds:
             emb.set_image(url=msg.embeds[0].image.url)
        emb.timestamp = msg.created_at
        return emb

    async def count_caramels(self, msg):
        n = 0
        u = []
        for r in msg.reactions:
            if 'caramel' in r.emoji.name:
                async for user in r.users():
                    if user.id not in u:
                        n += 1
                        u.append(user.id)
        return n

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Caramelboard(bot))
