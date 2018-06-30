from discord.ext import commands


def basic_cooldown(seconds):
    async def predicate(ctx):
        if ctx.invoked_with.lower() == 'help':
            return True
        key = f"cooldown:{ctx.author.id}:{ctx.command.qualified_name}"
        cooldown = await ctx.redis.ttl(key)
        if cooldown > 0:
            raise commands.CommandOnCooldown(None, cooldown)
        await ctx.redis.set(key, 1, expire=seconds)
        return True
    return commands.check(predicate)
