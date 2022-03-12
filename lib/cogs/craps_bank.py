import asyncio

from discord.ext.commands import Cog, command, cooldown, BucketType

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
                await ctx.send(f"Your current bankroll: ${balance:,.2f} {ctx.message.author.name}")

    @command(name="loadmoney", aliases=["load"])
    async def load_money(self, ctx, money: float):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            pass
        elif not isinstance(money, float):
            await ctx.send("Enter in a valid amount of money.")
        else:
            row = db.record("SELECT * FROM craps_board WHERE n_UserID = ?", ctx.message.author.id)
            if row is None:
                pass
            else:
                check_for_active_bets, = await asyncio.gather((CrapsBank.check_bets(self, ctx, row)))
                if check_for_active_bets is True:
                    await ctx.send(f"You've already placed bets down. {ctx.message.author.name}")
                    return

            point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
            if point is None:
                point = 0
            if point != 0:
                await ctx.send("Please wait until the roll ends to put your money down. Ingrate.")
            elif money > 500:
                await ctx.send("Bro.  You ain't that rich.  Keep it under 500 bucks.")
                return
            else:
                player_id = ctx.author.id
                balance = db.field("SELECT bankRoll FROM craps_bank WHERE UserID=?", player_id)
                if balance is None:
                    db.execute("INSERT INTO craps_bank(UserID,bankRoll) VALUES (?,?)", player_id, money)
                    await ctx.send(f"Your current bankroll: ${money:,.2f}")
                elif balance + money > 500:
                    if balance > 500:
                        await ctx.send(f"Max is 500 and you're already rich.")
                    else:
                        balance = 500
                        db.execute("UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, player_id)
                        await ctx.send(f"Your current bankroll: ${balance :,.2f} {ctx.author.name}")
                else:
                    db.execute("UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", (balance + money), player_id)
                    await ctx.send(f"Your current bankroll: ${(balance+money):,.2f} {ctx.author.name}")

    async def check_bets(self, ctx, row):
        all_bets = ""
        while all_bets == "":
            if row['i_pass'] != 0:
                all_bets += f"Pass ${row['i_pass']:,.2f}, "
                break
            if row['i_dont'] != 0:
                all_bets += f"Dont ${row['i_pass']:,.2f}, "
                break
            if row['i_pass_odds'] != 0:
                all_bets += f"Pass Odds ${row['i_pass_odds']:,.2f}, "
                break
            if row['i_dont_odds'] != 0:
                all_bets += f"Dont Pass Odds ${row['i_dont_odds']:,.2f}, "
                break
            if row['i_place_4'] != 0:
                all_bets += f"Place 4 ${row['i_place_4']:,.2f}, "
                break
            if row['i_place_5'] != 0:
                all_bets += f"Place 5 ${row['i_place_5']:,.2f}, "
                break
            if row['i_place_6'] != 0:
                all_bets += f"Place 6 ${row['i_place_6']:,.2f}, "
                break
            if row['i_place_8'] != 0:
                all_bets += f"Place 8 ${row['i_place_8']:,.2f}, "
                break
            if row['i_place_9'] != 0:
                all_bets += f"Place 9 ${row['i_place_9']:,.2f}, "
                break
            if row['i_place_10'] != 0:
                all_bets += f"Place 10 ${row['i_place_10']:,.2f}, "
                break
            if row['i_hard_4'] != 0:
                all_bets += f"Hard 4 ${row['i_hard_4']:,.2f}, "
                break
            if row['i_hard_6'] != 0:
                all_bets += f"Hard 6 ${row['i_hard_6']:,.2f}, "
                break
            if row['i_hard_8'] != 0:
                all_bets += f"Hard 8 ${row['i_hard_8']:,.2f}, "
                break
            if row['i_hard_10'] != 0:
                all_bets += f"Hard 10 ${row['i_hard_10']:,.2f}, "
                break
            if row['i_horn_2'] != 0:
                all_bets += f"Aces ${row['i_horn_2']:,.2f}, "
                break
            if row['i_horn_3'] != 0:
                all_bets += f"Acey Deucey ${row['i_horn_3']:,.2f}, "
                break
            if row['i_horn_11'] != 0:
                all_bets += f"Yooo ${row['i_horn_11']:,.2f}, "
                break
            if row['i_horn_12'] != 0:
                all_bets += f"Box Cars ${row['i_horn_12']:,.2f}, "
                break
            if row['i_horny'] != 0:
                all_bets += f"Horn bet ${row['i_horny']:,.2f}, "
                break
            if row['i_field'] != 0:
                all_bets += f"Field ${row['i_field']:,.2f}, "
                break
            if all_bets == "":
                all_bets = "a"
        if all_bets == "a":
            return False
        else:
            return True

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.craps_channel = self.bot.get_channel(946091566433456128)
            self.bot.cogs_ready.ready_up("craps_bank")


def setup(bot):
    bot.add_cog(CrapsBank(bot))
