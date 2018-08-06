import datetime
import re

import discord

INVITE_REGEX = "(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+"


class Automod:
    """Auto moderation"""

    def __init__(self, bot):
        self.bot = bot
        self.inviteregex = re.compile(INVITE_REGEX)

    async def on_member_join(self, member):
        if member.created_at > datetime.datetime.now() - datetime.timedelta(days=1):
            return await member.ban(reason="Auto-ban for suspicious account")
        invite = self.inviteregex.search(member.name)
        if invite:
            return await member.ban(reason="Auto-ban for invite link in username")

    async def on_message(self, msg):
        if msg.guild is None:
            return

        # Check if message content contains an invite url
        invite = self.inviteregex.search(msg.content)
        if invite:
            # Ignore staff though
            if discord.utils.get(msg.author.roles, name="Staff") is None:
                await msg.delete()
                await msg.channel.send(f"{msg.author.mention} you sent an invite link, I deleted it for you.")
                await msg.author.add_roles(discord.utils.get(msg.guild.roles, id=372846755626352641))


def setup(bot):
    bot.add_cog(Automod(bot))
