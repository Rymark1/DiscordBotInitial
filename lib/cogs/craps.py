import asyncio
import sqlite3
from datetime import datetime

from discord import Embed, File
from discord.ext.commands import Cog, command, cooldown
from random import choice, randint

from ..db import db


# help menu main class.  We control the look and feel of the pages as they show.
class Craps(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = self.bot.get_channel(941827777336836116)

    @command(name="bankroll")
    async def bankroll(self, ctx):
        # only work in craps channel
        if ctx.channel.id != 946091566433456128:
            pass
        else:
            playerID = ctx.author.id
            balance = db.field("SELECT bankRoll FROM craps WHERE UserID=?", playerID)
            if balance is None:
                await ctx.send(f"You've never played craps.  Start a session with 500 on the house.")
            else:
                await ctx.send(f"Your current bankroll: ${balance:,.2f}")

    @command(name="craps")
    @cooldown(1,100)
    async def play_craps(self, ctx, bet: float = 0.0):
        # only work in craps channel
        if ctx.channel.id != 946091566433456128:
            pass
        elif not isinstance(bet, float):
            await ctx.send("Please enter a numeric bet")
        else:
            playerID = ctx.author.id
            balance = db.field("SELECT bankRoll FROM craps WHERE UserID=?", playerID)
            if balance is None:
                balance = 500.0
                db.execute("INSERT INTO craps(UserID,bankRoll) VALUES (?,?)", playerID, 500.0)
            if balance <= 0.0:
                db.execute("UPDATE craps SET bankRoll = ? WHERE UserID = ?", 500.0, playerID)
                balance = 500.0
            # variable, returns the first element in the tuple as whatever type it current was defined as.
            bet, = await asyncio.gather((Craps.crapsgame(self, ctx, bet)))
            balance += bet
            db.execute("UPDATE craps SET bankRoll = ? WHERE UserID = ?", balance, playerID)
            if bet >= 0:
                await ctx.send(f"Your winnings: ${bet:,.2f} Current bankroll: ${balance:,.2f}")
            else:
                await ctx.send(f"You lost: ${bet:,.2f} Current bankroll: ${balance:,.2f}")
        self.play_craps.reset_cooldown(ctx)

    async def crapsgame(self, ctx, bet):
        insta_win = (7, 11)
        craps_nbrs = (2, 3, 12)

        rollnbr = 0
        point = 0
        comeout_roll = True
        player_done = False

        while not player_done:
            rollnbr += 1
            sum, = await asyncio.gather(Craps.craps_roll(self, ctx, rollnbr))

            if comeout_roll:
                if sum in insta_win:
                    bet *= 2
                    player_done = True
                elif sum in craps_nbrs:
                    bet *= -1
                    player_done = True
                else:
                    comeout_roll = False
                    point = sum
            else:
                if sum == point:
                    bet *= 2
                    player_done = True
                elif sum == 7:
                    bet *= -1
                    player_done = True
                else:
                    pass
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
