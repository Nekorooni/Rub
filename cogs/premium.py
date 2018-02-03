from functools import partial

import aiohttp
import discord
from PIL import Image, ImageDraw
from discord.ext import commands
from io import BytesIO

from cogs.inventory import needs_profile


def get_color_role(member):
    for role in member.roles:
        if role.color == member.color:
            return role

class Shop:
    __slots__ = ('name', 'items')

    def __init__(self, name):
        

class ShopItem:
    __slots__ = ('name', 'price', 'action')

    def __init__(self, name, price=0, action=None):
        self.name = name
        self.price = price
        self.action = action

    def __str__(self):
        return f'{self.name} {"- "+str(i.price)+" coins"  if i.price!=0 else ""}'

    async def buy(self):
        pass


shopitems = {
    'Event role colors': {
        'neptune': ShopItem('<@&396068839525187584>', 20000),
        'cirno': Item('<@&396075783803633674>', 15000),
        'shiina': Item('<@&391557036346834944>', 10000)
    },
    'Regular name colors': {
        'aa': Item('Coming soon~', 0),
    },
    'Functional': {
        'lewd': Item('Access to lewd channels', 100)
    }
}


class Premium:
    """Premium stuff for premium people"""

    def __init__(self, bot):
        self.bot = bot
        self.profiles = bot.get_cog('Profiles')
        self.session = aiohttp.ClientSession(loop=bot.loop)
        # create a ClientSession to be used for downloading avatars

    @commands.command()
    @commands.guild_only()
    @needs_profile()
    async def color(self, ctx, color: discord.Role):
        c = get_color_role(ctx.author)
        if await ctx.bot.db.fetchone(f'SELECT id FROM inventory '
                                     f'WHERE profile_id="{ctx.profile.pid}" '
                                     f'AND item_id="10" AND data="<@&{color.id}>"'):
            await ctx.author.remove_roles(c)
            await ctx.author.add_roles(color)
            await ctx.send("There you go!")
        else:
            await ctx.send("You don't have that coupon.")

    @commands.command()
    async def shop(self, ctx):
        profile = await self.profiles.get_profile(ctx.author.id, ['coins'])
        embed = {
            "title": "Welcome to the store!",
            "description": "Feel free to look around, to buy something type `!buy [item]`!",
            "color": 4902090,
            "footer": {
                # "icon_url": "https://cdn.discordapp.com/emojis/386689471002968075.png",
                "text": f"You have {profile.coins} coins"
            },
            "fields": [{'name': cat, 'value': '\n'.join([f'{i.name} {"- "+str(i.price)+" coins"  if i.price!=0 else ""}' for i in shopitems[cat].values()])} for cat in shopitems]
        }
        await ctx.send(embed=discord.Embed.from_data(embed))

    @commands.command()
    async def buy(self, ctx, item):
        item = {}

    @commands.command()
    async def profile(self, ctx, *, member: discord.Member = None):

        member = member or ctx.author
        # this means that if the user does not supply a member, it will default to the
        # author of the message.

        async with ctx.typing():
            # this means the bot will type while it is processing and uploading the image

            if isinstance(member, discord.Member):
                member_colour = member.colour.to_rgb()
                # get the user's colour, pretty self explanatory
            else:
                member_colour = (0, 0, 0)
                # if this is in a DM or something went seriously wrong

            avatar_bytes = await self.get_avatar(member)
            # grab the user's avatar as bytes

            fn = partial(self.processing, avatar_bytes, member_colour)
            # create partial function so we don't have to stack the args in run_in_executor

            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            # this runs our processing in an executor, stopping it from blocking the thread loop.
            # as we already seeked back the buffer in the other thread, we're good to go

            file = discord.File(filename="circle.png", fp=final_buffer)
            # prepare the file

            await ctx.send(file=file)
            # send it

    async def get_avatar(self, user) -> bytes:
        avatar_url = user.avatar_url_as(format="png", size=128)
        # generally an avatar will be 1024x1024, but we shouldn't rely on this

        async with self.session.get(avatar_url) as response:
            # this gives us our response object, and now we can read the bytes from it.
            avatar_bytes = await response.read()

        return avatar_bytes

    @staticmethod
    def processing(avatar_bytes: bytes, colour: tuple) -> BytesIO:
        with Image.open(BytesIO(avatar_bytes)) as im:
            # we must use BytesIO to load the image here as PIL expects a stream instead of
            # just raw bytes.

            with Image.new("RGB", im.size, colour) as background:
                # this creates a new image the same size as the user's avatar, with the
                # background colour being the user's colour.

                rgb_avatar = im.convert("RGB")
                # this ensures that the user's avatar lacks an alpha channel, as we're
                # going to be substituting our own here.

                with Image.new("RGBA", [400, 200], 0) as mask:
                    # this is the mask image we will be using to create the circle cutout
                    # effect on the avatar.

                    mask_draw = ImageDraw.Draw(mask)
                    # ImageDraw lets us draw on the image, in this instance, we will be
                    # using it to draw a white circle on the mask image.

                    mask_draw.ellipse([(0, 0), im.size], fill=255)
                    # draw the white circle from 0, 0 to the bottom right corner of the image

                    background.paste(rgb_avatar, (0, 0), mask=mask)
                    # paste the alpha-less avatar on the background using the new circle mask
                    # we just created.

                final_buffer = BytesIO()
                # prepare the stream to save this image into

                background.save(final_buffer, "png")
                # save into the stream, using png format.

        final_buffer.seek(0)
        # seek back to the start of the stream

        return final_buffer

def setup(bot):
    bot.add_cog(Premium(bot))
