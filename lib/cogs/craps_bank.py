from discord.ext.commands import Cog, command

from ..db import db


# help menu main class.  We control the look and feel of the pages as they show.
class CrapsBank(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="bankroll")
    async def bankroll(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            pass
        else:
            player_id = ctx.author.id
            balance = db.field("SELECT bankRoll FROM craps_bank WHERE UserID=?", player_id)
            if balance is None:
                await ctx.send("You've never played craps.  Load some money and chase the thrill!!")
            else:
                await ctx.send(f"Your current bankroll: ${balance:,.2f}")

    @command(name="loadmoney")
    async def load_money(self, ctx, money: float = 0.0):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            pass
        else:
            point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
            if point is None:
                point = 0
            if point != 0:
                await ctx.send("Please wait until the roll ends to put your money down. Ingrate.")
            else:
                player_id = ctx.author.id
                balance = db.field("SELECT bankRoll FROM craps_bank WHERE UserID=?", player_id)
                if balance is None:
                    db.execute("INSERT INTO craps_bank(UserID,bankRoll) VALUES (?,?)", player_id, money)
                    await ctx.send(f"Your current bankroll: ${money:,.2f}")
                else:
                    db.execute("UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", (balance + money), player_id)
                    await ctx.send(f"Your current bankroll: ${(balance+money):,.2f} {ctx.author.name}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.craps_channel = self.bot.get_channel(946091566433456128)
            self.bot.cogs_ready.ready_up("craps_bank")


def setup(bot):
    bot.add_cog(CrapsBank(bot))
