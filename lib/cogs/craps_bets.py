import asyncio
from typing import Optional

from discord.ext.commands import Cog, command, MissingRequiredArgument, cooldown, BucketType

from ..db import db


# help menu main class.  We control the look and feel of the pages as they show.
class CrapsBets(Cog):
    def __init__(self, bot):
        self.bot = bot

    # pass line bet can only happen while craps_bank is active and no point has been set.
    @command(name="passline")
    async def pass_bet(self, ctx, bet: int, remove: Optional[str] = ""):
        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        if point is not None and point != 0:
            await ctx.send("You can't bet the pass line once the come-out roll has happened.")
            return

        dont_pass = db.field("SELECT i_dont FROM craps_board WHERE n_UserID=?", 1)
        if dont_pass is None:
            dont_pass = 0
        if dont_pass != 0:
            await ctx.send("Don't bet on both the pass and dont pass dummy.")
            return

        point_info = db.record("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if point_info is None:
            db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", ctx.author.id)

        already_bet = db.field("SELECT i_pass FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if remove.lower() == "r":
            db.execute(f"UPDATE craps_board SET i_pass = ? WHERE n_UserID = ?", 0, ctx.author.id)
            balance += already_bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"${already_bet:,.2f} on the pass line is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
        elif already_bet is not None and already_bet != 0:
            db.execute(f"UPDATE craps_board SET i_pass = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
            await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} bet on the pass line. {ctx.author.name}. "
                           f" Balance is ${balance - bet:,.2f}.")
        else:
            db.execute(f"UPDATE craps_board SET i_pass = ? WHERE n_UserID = ?", bet, ctx.author.id)
            balance -= bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"${bet:,.2f} on the pass line is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    @command(name="dont")
    async def dont_pass_bet(self, ctx, bet: int, remove: Optional[str] = ""):
        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        if point is not None and point != 0:
            await ctx.send("You can't bet the don't pass line once the come-out roll has happened.")
            return

        pass_line = db.field("SELECT i_pass FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if pass_line is not None and pass_line > 0:
            await ctx.send("Don't bet on both the pass and dont pass dummy.")
            return

        point_info = db.record("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if point_info is None:
            db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", ctx.author.id)

        already_bet = db.field("SELECT i_dont FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if remove.lower() == "r":
            db.execute(f"UPDATE craps_board SET i_dont = ? WHERE n_UserID = ?", 0, ctx.author.id)
            balance += already_bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"${already_bet:,.2f} on the don't pass line is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
        elif already_bet is not None and already_bet != 0:
            db.execute(f"UPDATE craps_board SET i_dont = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
            await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} bet on the dont pass line."
                           f" {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
        else:
            db.execute(f"UPDATE craps_board SET i_dont = ? WHERE n_UserID = ?", bet, ctx.author.id)
            balance -= bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"${bet:,.2f} on the don't pass line is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    @command(name="odds")
    async def odds_bet(self, ctx, bet: int, remove: Optional[str] = ""):

        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        if point is None or point == 0:
            await ctx.send("You can't bet odds until after the come out roll.")
            return

        point_info = db.record("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if point_info is None or (point_info['i_pass'] == 0 and point_info['i_dont'] == 0):
            await ctx.send("You can't bet odds without a pass or don't pass line bet.")
            return
        pass_line = point_info[1]
        dont_pass_line = point_info[2]
        max_dont_odds = dont_pass_line * 6
        if point == 4 or point == 10:
            max_odds = pass_line * 3
        elif point == 5 or point == 9:
            max_odds = pass_line * 4
        elif point == 6 or point == 8:
            max_odds = pass_line * 5
        else:
            max_odds = 0
            await ctx.send("Something went wrong in the odds command")

        if pass_line > 0:
            if bet > max_odds:
                await ctx.send("You can't bet that much on odds.  We use the 3-4-5 system.")
                return
            else:
                already_bet = db.field("SELECT i_pass_odds FROM craps_board WHERE n_UserID=?", ctx.author.id)
                if remove.lower() == "r":
                    db.execute(f"UPDATE craps_board SET i_pass_odds = ? WHERE n_UserID = ?", 0, ctx.author.id)
                    balance += already_bet
                    db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                    await ctx.send(f"${already_bet:,.2f} on the pass odds is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
                elif already_bet is not None and already_bet != 0:
                    db.execute(f"UPDATE craps_board SET i_pass_odds = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
                    db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
                    await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} bet on pass odds "
                                   f" {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
                else:
                    db.execute(f"UPDATE craps_board SET i_pass_odds = ? WHERE n_UserID = ?", bet, ctx.author.id)
                    balance -= bet
                    db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                    await ctx.send(f"${bet:,.2f} on the pass odds is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")
        if dont_pass_line > 0:
            if bet > max_dont_odds:
                await ctx.send("You can't bet that much on odds.  The limit is 6x your bet.")
                return
            else:
                already_bet = db.field("SELECT i_dont_odds FROM craps_board WHERE n_UserID=?", ctx.author.id)
                if remove.lower() == "r":
                    db.execute(f"UPDATE craps_board SET i_dont_odds = ? WHERE n_UserID = ?", 0, ctx.author.id)
                    balance += already_bet
                    db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                    await ctx.send(f"${already_bet:,.2f} on the don't pass odds is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
                elif already_bet is not None and already_bet != 0:
                    db.execute(f"UPDATE craps_board SET i_dont_odds = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
                    db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
                    await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} bet on dont pass odds "
                                   f" {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
                else:
                    db.execute(f"UPDATE craps_board SET i_dont_odds = ? WHERE n_UserID = ?", bet, ctx.author.id)
                    balance -= bet
                    db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                    await ctx.send(f"${bet:,.2f} on the don't pass odds is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    @command(name="place")
    async def place_bet(self, ctx, number: int, bet: int, remove: Optional[str] = ""):
        valid = [4, 5, 6, 8, 9, 10]

        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        if point is None or point == 0:
            await ctx.send("Please wait until a valid point is hit " + ctx.author.name)
        elif number not in valid:
            await ctx.send("Please choose a valid point to bet on " + ctx.author.name)
        else:
            point_info = db.field("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
            if point_info is None:
                db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", ctx.author.id)
            db_var_name = "i_place_" + str(number)

            already_bet = db.field(f"SELECT {db_var_name} FROM craps_board WHERE n_UserID=?", ctx.author.id)
            if remove.lower() == "r":
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", 0, ctx.author.id)
                balance += already_bet
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                await ctx.send(f"${already_bet:,.2f} on the {str(number)} place bet is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
            elif already_bet is not None and already_bet != 0:
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
                await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} bet on the {str(number)} "
                               f"place bet. {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
            else:
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", bet, ctx.author.id)
                balance -= bet
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                await ctx.send(f"${bet:,.2f} on the {str(number)} place bet is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    @command(name="hard")
    async def hard_way_bet(self, ctx, number: int, bet: int, remove: Optional[str] = ""):
        valid = [4, 5, 6, 8, 10]

        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        if point is None or point == 0:
            await ctx.send("Please wait until a valid point is hit " + ctx.author.name)
        elif number not in valid:
            await ctx.send("Please choose a valid hardway to bet on " + ctx.author.name)
        else:
            point_info = db.field("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
            if point_info is None:
                db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", ctx.author.id)
            db_var_name = "i_hard_" + str(number)
            already_bet = db.field(f"SELECT {db_var_name} FROM craps_board WHERE n_UserID=?", ctx.author.id)
            if remove.lower() == "r":
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", 0, ctx.author.id)
                balance += already_bet
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                await ctx.send(f"${bet:,.2f} on the {str(number)} hardway bet is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
            elif already_bet is not None and already_bet != 0:
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
                await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} bet on the hard "
                               f"{str(number)} {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
            else:
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", bet, ctx.author.id)
                balance -= bet
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                await ctx.send(f"${bet:,.2f} on the {str(number)} hardway bet is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    @command(name="horn")
    async def horn_bet(self, ctx, number: int, bet:int, remove: Optional[str] = ""):
        valid = [2, 3, 11, 12]
       
        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        if number not in valid:
            await ctx.send("Please choose a valid horn number to bet on " + ctx.author.name)
        else:
            point_info = db.field("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
            if point_info is None:
                db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", ctx.author.id)
            db_var_name = "i_horn_" + str(number)
            already_bet = db.field(f"SELECT {db_var_name} FROM craps_board WHERE n_UserID=?", ctx.author.id)
            if remove.lower() == "r":
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", 0, ctx.author.id)
                balance += already_bet
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                await ctx.send(f"One time ${bet:,.2f} bet on the {str(number)} is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
            elif already_bet is not None and already_bet != 0:
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
                await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} one time bet on the "
                               f"{str(number)} {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
            else:
                db.execute(f"UPDATE craps_board SET {db_var_name} = ? WHERE n_UserID = ?", bet, ctx.author.id)
                balance -= bet
                db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
                await ctx.send(f"One time ${bet:,.2f} bet on the {str(number)} is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    @command(name="allhorn", aliases=["horny"])
    async def horn_all_bet(self, ctx, bet: int, remove: Optional[str] = ""):
        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        point_info = db.field("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if point_info is None:
            db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", ctx.author.id)

        already_bet = db.field("SELECT i_horny FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if remove.lower() == "r":
            db.execute("UPDATE craps_board SET i_horny = ? WHERE n_UserID = ?", 0, ctx.author.id)
            balance += already_bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"One time ${bet:,.2f} on the horn is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
        elif already_bet is not None and already_bet != 0:
            db.execute(f"UPDATE craps_board SET i_horny = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
            await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} horn bet"
                           f" {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
        else:
            db.execute(f"UPDATE craps_board SET i_horny = ? WHERE n_UserID = ?", bet, ctx.author.id)
            balance -= bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"One time ${bet:,.2f} on the horn is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    @command(name="evens")
    async def evens(self, ctx, bet: int, remove: Optional[str] = ""):
        await ctx.send(f"Skip, This is craps.")

    @command(name="field")
    async def horn_bet(self, ctx, bet:int, remove: Optional[str] = ""):
        check_list, = await asyncio.gather((CrapsBets.check_bet(self, ctx, bet, remove)))
        valid_bet = check_list[0]
        balance = check_list[1]
        if not valid_bet:
            return

        point_info = db.field("SELECT * FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if point_info is None:
            db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", ctx.author.id)

        already_bet = db.field("SELECT i_field FROM craps_board WHERE n_UserID=?", ctx.author.id)
        if remove.lower() == "r":
            db.execute("UPDATE craps_board SET i_field = ? WHERE n_UserID = ?", 0, ctx.author.id)
            balance += already_bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"One time ${bet:,.2f} on the horn is removed {ctx.author.name}. Balance is ${balance:,.2f}.")
        elif already_bet is not None and already_bet != 0:
            db.execute(f"UPDATE craps_board SET i_field = ? WHERE n_UserID = ?", bet + already_bet, ctx.author.id)
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance - bet, ctx.author.id)
            await ctx.send(f"You added ${bet:,.2f} to your existing ${already_bet:,.2f} field bet"
                           f" {ctx.author.name}.  Balance is ${balance - bet:,.2f}.")
        else:
            db.execute(f"UPDATE craps_board SET i_field = ? WHERE n_UserID = ?", bet, ctx.author.id)
            balance -= bet
            db.execute(f"UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, ctx.author.id)
            await ctx.send(f"One time ${bet:,.2f} bet on the field is accepted {ctx.author.name}. Balance is ${balance:,.2f}.")

    async def check_bet(self, ctx, bet: int, remove: str):
        if ctx.channel.id != self.craps_channel.id:
            return [False, 0]
        balance = db.field("SELECT bankRoll FROM craps_bank WHERE UserID=?", ctx.author.id)

        if isinstance(bet, float):
            await ctx.send("Get than fraction crap out of here.  Get it?")
            return [False, balance]
        elif not isinstance(bet, int):
            await ctx.send("Enter a valid amount for a bet that is a flat dollar amount.")
            return [False, balance]
        elif bet <= 0 and remove.lower() != "r":
            await ctx.send("Bet an amount greater than 0.")
            return [False, balance]
        elif balance is None or balance < bet:
            await ctx.send("Begone with that weak bankroll.  Get some more money.")
            return [False, balance]
        else:
            return [True, balance]

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.craps_channel = self.bot.get_channel(946091566433456128)
            self.bot.cogs_ready.ready_up("craps_bets")


def setup(bot):
    bot.add_cog(CrapsBets(bot))
