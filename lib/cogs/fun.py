from asyncio import sleep
from random import choice, randint

from aiohttp import request

from discord.ext.commands import Cog, BadArgument, BucketType
from discord.ext.commands import command, cooldown
from discord.errors import HTTPException
from discord import Member, Embed
from typing import Optional


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    # the choice function allows a variety of choices that will occur randomly.  Important to note that both sets of () are needed
    @command(name="hello", aliases=["hi"], brief="Introductions")
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Piss is as piss does', 'Yoooo'))} {ctx.author.mention}!")

    # Uses a random class to roll dice and output the results.
    @command(name="dice", brief="Roll Dice")
    # the arguments are (# of times command is called before cooldown, time in seconds, type or level of cooldown)
    @cooldown(1, 10, BucketType.user)
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

    @command(name="slap", aliases=["hit"], brief="Slap some peeps")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
        if member.id == self.bot.user.id:
            await ctx.send(f"{self.bot.user} slapped {ctx.author.name} for fun!")
        else:
            # to give the message time to process and load fully
            await sleep(1)
            await ctx.message.delete()
            await ctx.send(f"{ctx.author.name} slapped {member.display_name} {reason}!")

    @command(name="doctorate", aliases=["doc", "phd"], brief="Get a white coat!")
    async def doctorate(self, ctx, degree: Optional[str] = "failing"):
        curr_nickname = ctx.message.author.name
        await ctx.message.author.edit(nick=f"{curr_nickname}: Doctor of {degree}")
        await ctx.send(f"{ctx.author.name} Now has a degree from ASU in {degree}!")


    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Unable to find that member.")

    # bot deletes what you say, then relays it back at you
    @command(name="echo", aliases=["say"], brief="Shout into the void")
    @cooldown(1, 15, BucketType.guild)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    # First direct API request.  We load the URL, with the specific API which spits bad a string of raw data, then load
    # and use that if a positive status (200) is returned
    @command(name="fact", brief="Animal facts")
    @cooldown(3, 60, BucketType.guild)
    async def animal_fact(self, ctx, animal: str):
        if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET", image_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]
                else:
                    image_link = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    embed = Embed(title=f"{animal.title()} fact",
                                  description=data["fact"],
                                  color=ctx.author.colour)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)
                # old way, just passing the fact, now we are embedding it
                #                    await ctx.send(data["fact"])
                else:
                    await ctx.send(f"API returned a {response.status} status")
        else:
            await ctx.send("No facts are available for that animal")

    # We call the api and affix the pokemon name
    # once we have the postive hit via to 200 status, we can then load the data into pokemon data, then directly
    # reference the individual fields needed which are available in their api documentation.
    #

    # need to make optional argument not equal to None to start.  Otherwise null error occurs.
    @command(name="pokemon", aliases=["Pokémon"], brief="syntax is <pokemon name>, (<shiny> or <no>), [unown type] ")
    @cooldown(1, 10, BucketType.guild)
    async def pokemon_fact(self, ctx, pokemonname: str, shiny: str = " ", unowntype: Optional[str] = " "):
        URL = f"https://pokeapi.co/api/v2/pokemon/{pokemonname.lower()}"
        unowntype = unowntype.lower()
        shiny = " " if shiny.lower() != "shiny" else "shiny"
        shiny = shiny.lower()

        pokemonname = pokemonname.lower()
        async with request("GET", URL, headers={}) as response:
            if response.status == 200:
                pokemondata = await response.json()
                name = pokemondata["name"]
                height = pokemondata["height"] / 10
                weight = pokemondata["weight"] / 10

                # this is equivalent to combining them next to each other
                # sprites = pokemondata["sprites"]
                # sprites_url = sprites["front_default"]
                if pokemonname == "unown" and len(unowntype) == 1 and unowntype != " ":
                    if unowntype == "?":
                        unownnbr = 27
                    elif unowntype == "!":
                        unownnbr = 26
                    else:
                        unownnbr = ord(unowntype) - 97
                    if unownnbr < 0 or unownnbr > 27:
                        unownnbr = 0
                    unown_URL = pokemondata["forms"][unownnbr]["url"]
                    async with request("GET", unown_URL, headers={}) as response1:
                        response1.raise_for_status()
                        if response1.status == 200:
                            unowndata = await response1.json()
                            if shiny == "shiny":
                                sprites_url = unowndata["sprites"]["front_shiny"]
                            else:
                                sprites_url = unowndata["sprites"]["front_default"]
                elif shiny == "shiny":
                    sprites_url = pokemondata["sprites"]["front_shiny"]
                else:
                    sprites_url = pokemondata["sprites"]["front_default"]

                async with request("GET", sprites_url, headers={}) as response:
                    if response.status == 200:
                        embed = Embed(title=f"{shiny} {pokemonname}",
                                      color=ctx.author.colour)
                        embed.set_image(url=sprites_url)
                        await ctx.send(embed=embed)

                await ctx.send(f"{name} weighs {weight}kg and is {height} meters tall")
            else:
                await ctx.send(f"API returned a {response.status} status")

    @pokemon_fact.error
    async def pokemon_fact_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("Please enter valid/all arguments")

    @command(name="rps", brief="Rock Paper Scissors")
    async def rock_paper_scissors(self, ctx, playerthrow: str):
        accepted_strings = {'rock', 'paper', "scissors"}
        # assigned playerthrow.lower() to playerthrow inline
        if (playerthrow := playerthrow.lower()) in accepted_strings:
            cputhrow = choice(('rock', 'paper', 'scissors'))
            if cputhrow == playerthrow:
                await ctx.send(
                    f"{ctx.author.name} threw {playerthrow} and {self.bot.user} threw {cputhrow}.  You tied!")
            else:
                if (cputhrow == "rock" and playerthrow == "scissors") or \
                        (cputhrow == "paper" and playerthrow == "rock") or \
                        (cputhrow == "scissors" and playerthrow == "paper"):
                    await ctx.send(f"{ctx.author.name} threw {playerthrow} and {self.bot.user} threw {cputhrow}.  You "
                                   f"lose.")
                else:
                    await ctx.send(f"{ctx.author.name} threw {playerthrow} and {self.bot.user} threw {cputhrow}.  You "
                                   f"win.")
        else:
            await ctx.send(f"Please enter a valid throw.")

    @command(name="gamble", brief="Win the Lottery")
    async def gamble(self, ctx, number: int):
        winningnbr = randint(1, randint(1, 1000))
        if number is winningnbr:
            await ctx.send(f"Congrats {ctx.author.name}!  Ryan owes you a dollar.")
        else:
            await ctx.send("Please venmo Ryan a dollar or the police will arrive at your house shortly.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
