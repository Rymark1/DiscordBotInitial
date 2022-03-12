import asyncio
from datetime import datetime

from _sqlite3 import OperationalError, Error
from discord import Embed, File
from discord.ext.commands import Cog, command, cooldown, has_permissions, CheckFailure, BucketType
from random import choice, randint

from ..db import db


# help menu main class.  We control the look and feel of the pages as they show.
class Craps(Cog):
    def __init__(self, bot):
        self.bot = bot

    # this command will start craps.  From there we'll have the 1 table row that will now exist.
    # It will allow bets to be placed.
    @command(name="startcraps")
    @has_permissions(manage_guild=True)
    async def start_craps(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            return

        try:
            rows_current = db.records("SELECT * FROM craps_current")
            if rows_current is not None:
                db.execute("""DELETE FROM craps_current""")
        except Error:
            pass

        try:
            rows_board = db.records("SELECT * FROM craps_board")
            if rows_board is not None:
                db.execute("""DELETE FROM craps_board""")
        except Error:
            pass

        db.execute("INSERT INTO craps_current (n_dummy) VALUES (?)", 1)
        await ctx.send("Welcome to Craps.  Everyone place your passline bets and a shooter will be selected.  "
                       "Once all bets are in, use the command 'shooter''.")

    @command(name="restartcraps")
    @has_permissions(manage_guild=True)
    async def restart_craps(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            return

        try:
            rows_current = db.records("SELECT * FROM craps_current")
            if rows_current is not None:
                db.execute("""DELETE FROM craps_current""")
        except Error:
            pass

        try:
            rows_board = db.records("SELECT * FROM craps_board")
            if rows_board is not None:
                db.execute("""DELETE FROM craps_board""")
        except Error:
            pass

        await ctx.send("Craps reset.")

    @restart_craps.error
    async def restart_craps_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("You need the Manage permission to do that.")

    @command(name="restartbank")
    @has_permissions(manage_guild=True)
    async def restart_bankroll(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            return

        try:
            rows_bank = db.records("SELECT * FROM craps_bank")
            if rows_bank is not None:
                db.execute("""DELETE FROM craps_bank""")
        except Error:
            pass
        await ctx.send("Bankroll reset.")

    @restart_bankroll.error
    async def restart_bankroll_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("You need the Manage permission to do that.")

    @command(name="status")
    async def status(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            return

        row = db.record("SELECT * FROM craps_current WHERE n_dummy = ?", 1)
        shooter_id = point = roll_nbr = 0
        if row['b_shooter'] is None:
            shooter_id = 0
        if row['i_point'] is None:
            point = 0
        if row['i_roll_nbr'] is None:
            roll_nbr = 0
        if row['b_shooter'] is None or row['b_shooter'] == 0:
            await ctx.send(f"""Current point: {row['i_point']}\tCurrent shooter: N/A\tCurrent roll: {row['i_roll_nbr']}""")
        else:
            user = self.bot.get_user(row['b_shooter'])
            await ctx.send(f"""Current point: {row['i_point']}\tCurrent shooter: {user.name}\tCurrent roll: {row['i_roll_nbr']}""")

    # this command will start craps.  From there we'll have the 1 table row that will now exist.
    # It will allow bets to be placed.
    @command(name="shooter")
    async def choose_shooter(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            return

        curr_shooter = db.field("SELECT b_shooter FROM craps_current WHERE n_dummy=?", 1)
        if curr_shooter is not None and curr_shooter != 0:
            if ctx.message.author.id != curr_shooter:
                await ctx.send(f"Only the shooter can pass the dice {ctx.message.author.name}")
                return

        shooters = []
        rows = db.records("SELECT * FROM craps_board")
        for row in rows:
            if row['i_pass'] != 0:
                shooters.append(row['n_UserID'])
        if shooters[0] is None:
            await ctx.send("No one has bet on the pass line.")
            return
        shooter_id = randint(0, len(shooters)-1)
        db.execute("UPDATE craps_current SET b_shooter = ? WHERE n_dummy = ?", shooters[shooter_id], 1)
        user = self.bot.get_user(shooters[shooter_id])
        await ctx.send("The shooter is " + user.name)

    @command(name="bets")
    async def print_current_board(self,ctx):
        rows = db.records("SELECT * FROM craps_board")

        for row in rows:
            all_bets = ""
            if row['i_pass'] != 0:
                all_bets += f"Pass ${row['i_pass']:,.2f}, "
            if row['i_dont'] != 0:
                all_bets += f"Dont ${row['i_pass']:,.2f}, "
            if row['i_pass_odds'] != 0:
                all_bets += f"Pass Odds ${row['i_pass_odds']:,.2f}, "
            if row['i_dont_odds'] != 0:
                all_bets += f"Dont Pass Odds ${row['i_dont_odds']:,.2f}, "
            if row['i_place_4'] != 0:
                all_bets += f"Place 4 ${row['i_place_4']:,.2f}, "
            if row['i_place_5'] != 0:
                all_bets += f"Place 5 ${row['i_place_5']:,.2f}, "
            if row['i_place_6'] != 0:
                all_bets += f"Place 6 ${row['i_place_6']:,.2f}, "
            if row['i_place_8'] != 0:
                all_bets += f"Place 8 ${row['i_place_8']:,.2f}, "
            if row['i_place_9'] != 0:
                all_bets += f"Place 9 ${row['i_place_9']:,.2f}, "
            if row['i_place_10'] != 0:
                all_bets += f"Place 10 ${row['i_place_10']:,.2f}, "
            if row['i_hard_4'] != 0:
                all_bets += f"Hard 4 ${row['i_hard_4']:,.2f}, "
            if row['i_hard_6'] != 0:
                all_bets += f"Hard 6 ${row['i_hard_6']:,.2f}, "
            if row['i_hard_8'] != 0:
                all_bets += f"Hard 8 ${row['i_hard_8']:,.2f}, "
            if row['i_hard_10'] != 0:
                all_bets += f"Hard 10 ${row['i_hard_10']:,.2f}, "
            if row['i_horn_2'] != 0:
                all_bets += f"Aces ${row['i_horn_2']:,.2f}, "
            if row['i_horn_3'] != 0:
                all_bets += f"Acey Deucey ${row['i_horn_3']:,.2f}, "
            if row['i_horn_11'] != 0:
                all_bets += f"Yooo ${row['i_horn_11']:,.2f}, "
            if row['i_horn_12'] != 0:
                all_bets += f"Box Cars ${row['i_horn_12']:,.2f}, "
            if row['i_horny'] != 0:
                all_bets += f"Horn bet ${row['i_horny']:,.2f}, "
            if row['i_field'] != 0:
                all_bets += f"Field ${row['i_field']:,.2f}, "
            if all_bets != "":
                all_bets = all_bets[:-2]
                user = self.bot.get_user(row['n_UserID'])
                await ctx.send(f"{user.name} - {all_bets}")

    # this command will start craps.  From there we'll have the 1 table row that will now exist.
    # It will allow bets to be placed.
    @command(name="roll")
    @cooldown(1, 10, BucketType.user)
    async def roll_dice(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            return
        shooter_id = db.field("SELECT b_shooter FROM craps_current WHERE n_dummy=?", 1)
        if shooter_id is None:
            await ctx.send("Shooter hasn't been chosen yet.")
            return
        if ctx.author.id != shooter_id:
            await ctx.send(ctx.author.name + " You are not the shooter.  Stop.")
            return

        # updating current die roll
        die_roll = db.field("SELECT i_roll_nbr FROM craps_current WHERE n_dummy=?", 1) + 1
        db.execute("UPDATE craps_current SET i_roll_nbr = ? WHERE n_dummy = ?", die_roll, 1)

        # printing bets, then waiting 4 seconds, then rolling
        await ctx.send("Current Bets on the board:")
        await asyncio.gather((Craps.print_current_board(self, ctx)))
        await asyncio.sleep(4)

        # Getting dice roll
        die1 = randint(1, 6)
        die2 = randint(1, 6)
        sum_of_dice = die1 + die2

        # embedding image to return dice roll
        die_roll_url = f"{str(die1)}{str(die2)}.png"
        embed = Embed(title=f"Roll {die_roll}",
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())

        file = File(f"./data/images/{die_roll_url}", filename="image.png")
        embed.set_image(url="attachment://image.png")
        phrase, = await asyncio.gather((Craps.choose_phrase(self, ctx, die1, die2)))
        embed.set_footer(text=phrase)
        await ctx.send(file=file, embed=embed)
        await asyncio.gather((Craps.send_outcome_message(self, ctx, die1, die2)))

        await asyncio.gather((Craps.resolve_bets(self, ctx, die1, die2)))

    async def choose_phrase(self, ctx, die1, die2):
        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        comeout_roll = True if point == 0 else False
        
        sum_of_dice = die1 + die2
        two_phrases = ["Craps", "eye balls", "two aces", "rats eyes", "snake eyes", "push the don’t",
                       "eleven in a shoe store", "twice in the rice", "two craps two two bad boys from Illinois",
                       "two crap aces", "aces in both places", "a spot and a dot", "dimples."]
        three_phrases = ["Craps", "ace-deuce", "three craps ace caught a deuce no use", "divorce roll come up single",
                         "winner on the dark side", "three craps three the indicator", "crap and a half flip side ‘O Yo",
                         "small ace deuce can’t produce", "the other side of eleven’s tummy", "three craps the middle",
                         "two-one son of a gun."]
        four_phrases = ["Little Joe", "little Joe from Kokomo", "ace trey the easy way"]
        five_phrases = ["After five the field’s alive", "little Phoebe", "fiver fiver racetrack driver", 
                        "we got the fever", "five fever", "five no field five."]
        six_phrases = ["Big Red catch’em in the corner", "like a blue chip stock", "the national average", 
                       "sixie from Dixie."]

        seven_16_phrases = ["Seven out line away", "grab the money", "seven’s a bruiser the front line’s a loser", 
                            "Benny Blue you’re all through", "six-ace you lost the race", "Six-ace in your face",
                            "six ace end of the race", "six one you’re all done", "up pops the devil"]
        seven_25_phrases = ["Seven out line away", "grab the money", "seven’s a bruiser the front line’s a loser", 
                            "Benny Blue you’re all through", "up pops the devil", "five two you’re all through"]
        seven_34_phrases = ["Seven out line away", "grab the money", "seven’s a bruiser the front line’s a loser", 
                            "Benny Blue you’re all through","three-four now we’re poor", 
                            "three-four we’ve lost the war.", "up pops the devil", "four-three woe is me"]
        eight_phrases = ["Ozzie and Harriet", "Donnie and Marie", "eighter from Decatur.", "eight is great"]
        nine_phrases = ["Center field", "center of the garden", "ocean liner niner", "Nina from Pasadena",
                        "Nina Niner wine and dine her"]
        nine_45_phrases = ["Center field", "center of the garden", "ocean liner niner", "Nina from Pasadena",
                           "Nina Niner wine and dine her", "What shot Jesse James? A forty-five."]
        ten_phrases = ["the big one on the end", "sixty-four out the door.", "I got a 10er for you", 
                       "fourty-six drops like the iron curtain"]
        eleven_phrases = ["Yo leven", "yo levine the dancing queen", "six five no jive",
                          "it’s not my eleven it’s yo eleven."]
        twelve_phrases = ["Craps", "boxcars", "atomic craps", "a whole lot of crap", "craps to the max",
                          "12 craps it’s crap unless you’re betting on it", "all the spots we got",
                          "all the spots and all the dots", "all the crap there is", "outstanding in your field",
                          "triple dipple in the lucky ducky", "midnight", "double saw on boxcars", "Crapus Maximus."]
        seven_front_winner = ["Seven Front Line Winner", "Take the Donts Pay the Line", "Big Red saves the day"
                              "Screw the donts", "Take the darkside"]
        eleven_front_winner = ["Eleven Front Line Winner", "Take the Donts Pay the Line", "Yo that front line"]

        four_hard = ["four the hard way", "two spots and two dots.", "hit us in the tu tu", "Double deuce"]
        six_hard = ["six the hard way", "pair-o-treys waiter’s roll", "Brooklyn Forest", 
                    "watch the Rhineland, its thirty-three"]
        eight_hard = ["eight the hard way",  "the windows", "A square pair like mom and dad"]
        ten_hard = ["ten the hard way", "Puppy paws", "pair-a-roses", "pair of sunflowers", "fifty-five to stay alive",
                    "two stars from mars"]

        if sum_of_dice == 2:
            return choice(two_phrases)
        elif sum_of_dice == 3:
            return choice(three_phrases)
        elif sum_of_dice == 4:
            if die1 == 2 and die2 == 2:
                return choice(four_hard)
            else:
                return choice(four_phrases)
        elif sum_of_dice == 5:
            return choice(five_phrases)
        elif sum_of_dice == 6:
            if die1 == 3 and die2 == 3:
                return choice(six_hard)
            else:
                return choice(six_phrases)
        elif sum_of_dice == 7:
            if comeout_roll:
                return choice(seven_front_winner)
            elif die1 == 1 or die2 == 1:
                return choice(seven_16_phrases)
            elif die1 == 2 or die2 == 2:
                return choice(seven_25_phrases)
            elif die1 == 3 or die2 == 3:
                return choice(seven_34_phrases)
        elif sum_of_dice == 8:
            if die1 == 4 and die2 == 4:
                return choice(eight_hard)
            else:
                return choice(eight_phrases)
        elif sum_of_dice == 9:
            if die1 == 4 or die2 == 4:
                return choice(nine_45_phrases)
            else:
                return choice(nine_phrases)
        elif sum_of_dice == 10:
            if die1 == 5 and die2 == 5:
                return choice(ten_hard)
            else:
                return choice(ten_phrases)
        elif sum_of_dice == 11:
            if comeout_roll:
                return choice(eleven_front_winner)
            else:
                return choice(eleven_phrases)
        elif sum_of_dice == 12:
            return choice(twelve_phrases)

    async def send_outcome_message(self, ctx, die1, die2):
        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        comeout_roll = True if point == 0 else False

        sum_of_dice = die1 + die2
        
        come_out_win_phrases = ["front line winner back line skinner", "Winner Winner, pay the line", "pay that line"]
        come_out_lose_phrases = ["Craps, front line loser", "Pay the Don'ts", "The Dark side wins this roll"]
        point_hits = ["Point hit, hot shooter", "Pay the front line, thats a winner", 
                      "Won't someone think of the Casinos profits."]
        big_red = ["Shooter out", "Better luck next round", "Pay the donts"]

        if comeout_roll:
            if sum_of_dice <= 3 or sum_of_dice == 12:
                await ctx.send(choice(come_out_lose_phrases))
            elif sum_of_dice == 7 or sum_of_dice == 11:
                await ctx.send(choice(come_out_win_phrases))
        elif sum_of_dice == 7:
            await ctx.send(choice(big_red))
        elif point == sum_of_dice:
            await ctx.send(choice(point_hits))
                
    async def resolve_bets(self, ctx, die1, die2):
        sum_of_dice = die1 + die2
        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        comeout_roll = True if point == 0 else False

        rows = db.records("SELECT * FROM craps_board")
        for row in rows:
            winnings = 0

            # resolve comeout pass/dont pass roll
            if comeout_roll:
                if sum_of_dice == 7 or sum_of_dice == 11:
                    winnings += row['i_pass']
                    db.execute("UPDATE craps_board SET i_dont=(?) WHERE n_UserID=(?)", 0, row['n_UserID'])
                elif sum_of_dice == 2 or sum_of_dice == 3 or sum_of_dice == 12:
                    winnings += row['i_dont']
                    db.execute("UPDATE craps_board SET i_pass=(?) WHERE n_UserID=(?)", 0, row['n_UserID'])
                else:
                    db.execute("UPDATE craps_current SET i_point = ? WHERE n_dummy = ?", sum_of_dice, 1)

            # resolve field bet.
            if (2 <= sum_of_dice <= 4) or (9 <= sum_of_dice <= 12):
                if sum_of_dice == 2:
                    winnings += row['i_field'] * 3
                elif sum_of_dice == 12:
                    winnings += row['i_field'] * 4
                else:
                    winnings += row['i_field'] * 2
            db.execute("UPDATE craps_board SET i_field=(?) WHERE n_UserID=(?)", 0, row['n_UserID'])

            # resolve horn bets.
            # if horny bet hit, split bet up and place on that number.
            if sum_of_dice == 2:
                winnings += row['i_horn_2'] * 31
                winnings += row['i_horny'] / 4 * 30
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                                WHERE n_UserID =(?)""", row['i_horny']/4, 0, 0, 0, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                            WHERE n_UserID =(?)""", row['i_horn_3'], 0, 0, 0, row['n_UserID'])
            elif sum_of_dice == 3:
                winnings += row['i_horn_3'] * 16
                winnings += row['i_horny'] / 4 * 15
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                                WHERE n_UserID =(?)""", 0, row['i_horny']/4, 0, 0, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                            WHERE n_UserID =(?)""", 0, row['i_horn_3'], 0, 0, row['n_UserID'])
            elif sum_of_dice == 11:
                winnings += row['i_horn_11'] * 16
                winnings += row['i_horny'] / 4 * 15
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                                WHERE n_UserID =(?)""", 0, 0, row['i_horny']/4, 0, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                            WHERE n_UserID =(?)""", 0, 0, row['i_horn_11'], 0, row['n_UserID'])
            elif sum_of_dice == 12:
                winnings += row['i_horn_12'] * 30
                winnings += row['i_horny'] / 4 * 30
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                                WHERE n_UserID =(?)""", 0, 0, 0, row['i_horny']/4, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?)
                            WHERE n_UserID =(?)""", 0, 0, 0, row['i_horn_12'], row['n_UserID'])
            else:
                db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                            WHERE n_UserID =(?)""", 0, 0, 0, 0, 0, row['n_UserID'])
            # resolve hardways and remove the bet if lost
            # also resolving place bets
            if not comeout_roll:
                if sum_of_dice == 7:
                    winnings += row['i_dont'] * 2
                    if sum_of_dice == 4 or sum_of_dice == 10:
                        winnings += row['i_dont_odds'] + row['i_dont_odds'] * 1/2
                    elif sum_of_dice == 5 or sum_of_dice == 9:
                        winnings += row['i_dont_odds'] + row['i_dont_odds'] * 2/3
                    elif sum_of_dice == 6 or sum_of_dice == 8:
                        winnings += row['i_dont_odds'] + row['i_dont_odds'] * 5/6
                    user_id = row['n_UserID']
                    db.execute("DELETE FROM craps_board WHERE n_UserID=?", user_id)
                    db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", user_id)
                    db.execute("UPDATE craps_current SET b_shooter = ?, i_point = ?, i_roll_nbr = ?"
                               " WHERE n_dummy = ?", 0, 0, 0, 1)
                elif sum_of_dice == 4:
                    if die1 == 2 and die2 == 2:
                        winnings += row['i_hard_4'] * 8
                    db.execute("UPDATE craps_board SET i_hard_4 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_4'] * 9/5
                elif sum_of_dice == 5:
                    winnings += row['i_place_5'] * 7/5
                elif sum_of_dice == 6:
                    if die1 == 3 and die2 == 3:
                        winnings += row['i_hard_6'] * 10
                    db.execute("UPDATE craps_board SET i_hard_6 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_6'] * 7/6
                elif sum_of_dice == 8:
                    if die1 == 4 and die2 == 4:
                        winnings += row['i_hard_8'] * 10
                    db.execute("UPDATE craps_board SET i_hard_8 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_8'] * 7/6
                elif sum_of_dice == 9:
                    winnings += row['i_place_9'] * 7/5
                elif sum_of_dice == 10:
                    if die1 == 5 and die2 == 5:
                        winnings += row['i_hard_10'] * 8
                    db.execute("UPDATE craps_board SET i_hard_10 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_10'] * 9/5 
                if sum_of_dice == point:
                    winnings += row['i_pass'] * 2
                    if sum_of_dice == 4 or sum_of_dice == 10:
                        winnings += row['i_pass_odds'] + row['i_pass_odds'] * 2
                    elif sum_of_dice == 5 or sum_of_dice == 9:
                        winnings += row['i_pass_odds'] + row['i_pass_odds'] * 3/2
                    elif sum_of_dice == 6 or sum_of_dice == 8:
                        winnings += row['i_pass_odds'] + row['i_pass_odds'] * 6/5
                    db.execute("UPDATE craps_board SET i_pass=(?), i_dont=(?), i_pass_odds=(?), i_dont_odds=(?) "
                               "WHERE n_UserID = (?)", 0, 0, 0, 0, row['n_UserID'])
                    db.execute("UPDATE craps_current SET i_point = ?, i_roll_nbr = ?"
                               " WHERE n_dummy = ?", 0, 0, 1)
            if winnings > 0:
                balance = db.field("SELECT bankRoll FROM craps_bank WHERE UserID=?", row['n_UserID'])
                balance += winnings
                db.execute("UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, row['n_UserID'])
                user = self.bot.get_user(row['n_UserID'])
                await ctx.send(f"""{user.name}\nWinnings: ${winnings:,.2f}\nCurrent bankroll: ${balance:,.2f}""")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.craps_channel = self.bot.get_channel(946091566433456128)
            self.bot.cogs_ready.ready_up("craps")


def setup(bot):
    bot.add_cog(Craps(bot))
