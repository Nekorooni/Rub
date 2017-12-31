import discord
from discord.ext import commands
# basic dependencies


import aiohttp
# aiohttp should be installed if discord.py is

from PIL import Image, ImageDraw
# PIL can be installed through
# `pip install -U Pillow`


from functools import partial
# partial lets us prepare a new function with args for run_in_executor

from io import BytesIO
# BytesIO allows us to convert bytes into a file-like byte stream.

from typing import Union


# this just allows for nice function annotation, and stops my IDE from complaining.


class ImageCog:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # we need to include a reference to the bot here so we can access its loop later.
        self.session = aiohttp.ClientSession(loop=bot.loop)
        # create a ClientSession to be used for downloading avatars

    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> bytes:
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

                with Image.new("L", im.size, 0) as mask:
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

    @commands.command()
    async def circle(self, ctx, *, member: discord.Member = None):
        """Display the user's avatar on their colour."""

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


def setup(bot: commands.Bot):
    # setup function so this can be loaded as an extension
    bot.add_cog(ImageCog(bot))