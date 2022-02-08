from random import choice, randint

from discord.ext.commands import Cog, BadArgument
from discord.ext.commands import command
from discord.errors import HTTPException
from discord import Member
from typing import Optional


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    # the choice function allows a variety of choices that will occur randomly.  Important to note that both sets of () are needed
    @command(name="hello", aliases=["hi"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Piss is as piss does', 'Yoooo'))} {ctx.author.mention}!")

    # Uses a random class to roll dice and output the results.
    @command(name="dice", aliases=["roll"])
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))
        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]

            await ctx.send(ctx.author.mention + "  " + " + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
        else:
            await ctx.send("Please limit number of dice between 1 -25.")

    # # outputs the error if we get an http error sent back.  Probably better to do that with a limiting on the dice
    # # they can choose, but I'm learnings so here we are
    # @roll_dice.error
    # async def roll_dice_error(self, ctx, exc):
    #     if isinstance(exc.original, HTTPException):
    #         await ctx.send("results overflow error. Please try a lower number.")

    # +slap @username for being a twat
    # the argument * makes it so "for being a twat" is a single argument
    # reason argument means that it doesn't have to be there
    # author.name returns username
    # author.display_name returns name inside server
    # author.mention returns the @username

    @command(name="slap", aliases=["hit"])
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
        if member.id == self.bot.user.id:
            await ctx.send(f"{self.bot.user} slapped {ctx.author.name} for fun!")
        else:
            await ctx.message.delete()
            await ctx.send(f"{ctx.author.name} slapped {member.display_name} {reason}!")

    @slap_member.error
    async def slap_member_error(self, ctx,exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Unable to find that member.")

    # bot deletes what you say, then relays it back at you
    @command(name="echo", aliases=["say"])
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
