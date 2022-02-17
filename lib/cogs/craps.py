import asyncio
from datetime import datetime

from discord import Embed, File
from discord.ext.commands import Cog, command
from random import choice, randint


# help menu main class.  We control the look and feel of the pages as they show.
class Craps(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = self.bot.get_channel(941827777336836116)


    @command(name="craps")
    async def play_craps(self, ctx, bet: float = 0.0):
        if not isinstance(bet, float):
            await ctx.send("Please enter a numeric bet")
        else:
            bet = await asyncio.gather((Craps.crapsgame(self, ctx, bet)))
            await ctx.send(f"Your winnings: {bet}")

    async def crapsgame(self, ctx, bet):
        rollnbr = 0
        comeout_roll = True
        playerlose = False

        while not playerlose:
            rollnbr += 1
            sum = await asyncio.gather(Craps.craps_roll(self, ctx, rollnbr))
            playerlose = True
            # if comeout_roll:
            #     if sum == 7 or 11:
            #         await ctx.send
        return bet

    async def craps_roll (self, ctx, rollnbr):
        die1 = randint(1,6)
        die2 = randint(1,6)
        sum = die1 + die2
        picchoice = ['a']
        if sum == 7:
            picchoice += ['f']
        if 6 <= sum <= 8:
            picchoice += ['e']
        if 5 <= sum <= 9:
            picchoice += ['d']
        if 4 <= sum <= 10:
            picchoice += ['c']
        if 3 <= sum <= 11:
            picchoice += ['b']

        dieroll_url = "dieroll" + str(sum) + str((choice(picchoice))) + ".png"
        await asyncio.gather(Craps.send_dice(self, ctx, rollnbr, dieroll_url))
        return sum

    async def send_dice(self, ctx, rollnbr, url):
        embed = Embed(title=f"Roll {rollnbr}",
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())

        file = File(f"./data/images/{url}", filename="image.png")

        embed.set_image(url="attachment://image.png")
        await ctx.send(file=file, embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("craps")


def setup(bot):
    bot.add_cog(Craps(bot))
