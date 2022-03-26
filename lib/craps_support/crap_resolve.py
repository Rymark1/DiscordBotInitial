import asyncio

from lib.db import db

MASTER_RECORD = 1


class CrapsResolve:

    async def resolve_bets(self, ctx, die1, die2):
        dice_sum = die1 + die2
        board_list = await asyncio.gather(CrapsResolve.get_master_record(self, ctx))
        point, shooter, current_roll, user = board_list[0]
        comeout_roll = (point == 0)

        rows = db.records("SELECT * FROM craps_board")
        for row in rows:
            winnings = 0
            
            # resolve comeout pass/dont pass roll
            if comeout_roll:
                if dice_sum == 7 or dice_sum == 11:
                    winnings += row['i_pass']
                    db.execute("UPDATE craps_board SET i_dont=(?) WHERE n_UserID=(?)", 0, row['n_UserID'])
                elif dice_sum == 2 or dice_sum == 3 or dice_sum == 12:
                    winnings += row['i_dont']
                    db.execute("UPDATE craps_board SET i_pass=(?) WHERE n_UserID=(?)", 0, row['n_UserID'])

            # resolve field bet.
            if (2 <= dice_sum <= 4) or (9 <= dice_sum <= 12):
                if dice_sum == 2:
                    winnings += row['i_field'] * 3
                elif dice_sum == 12:
                    winnings += row['i_field'] * 4
                else:
                    winnings += row['i_field'] * 2
            db.execute("UPDATE craps_board SET i_field=(?) WHERE n_UserID=(?)", 0, row['n_UserID'])

            # resolve horn bets.
            # if horny bet hit, split bet up and place on that number.
            if dice_sum == 2:
                winnings += row['i_horn_2'] * 31
                winnings += row['i_horny'] / 4 * 30
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                                WHERE n_UserID =(?)""", row['i_horny']/4, 0, 0, 0, 0, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                            WHERE n_UserID =(?)""", row['i_horn_3'], 0, 0, 0, 0, row['n_UserID'])
            elif dice_sum == 3:
                winnings += row['i_horn_3'] * 16
                winnings += row['i_horny'] / 4 * 15
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                                WHERE n_UserID =(?)""", 0, row['i_horny']/4, 0, 0, 0, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                            WHERE n_UserID =(?)""", 0, row['i_horn_3'], 0, 0, 0, row['n_UserID'])
            elif dice_sum == 11:
                winnings += row['i_horn_11'] * 16
                winnings += row['i_horny'] / 4 * 15
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                                WHERE n_UserID =(?)""", 0, 0, row['i_horny']/4, 0, 0, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                            WHERE n_UserID =(?)""", 0, 0, row['i_horn_11'], 0, 0, row['n_UserID'])
            elif dice_sum == 12:
                winnings += row['i_horn_12'] * 30
                winnings += row['i_horny'] / 4 * 30
                if row['i_horny'] != 0:
                    db.execute("""UPDATE craps_board  
                                SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                                WHERE n_UserID =(?)""", 0, 0, 0, row['i_horny']/4, 0, row['n_UserID'])
                else:
                    db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                            WHERE n_UserID =(?)""", 0, 0, 0, row['i_horn_12'], 0, row['n_UserID'])
            else:
                db.execute("""UPDATE craps_board  
                            SET i_horn_2=(?), i_horn_3=(?), i_horn_11=(?), i_horn_12=(?), i_horny=(?)
                            WHERE n_UserID =(?)""", 0, 0, 0, 0, 0, row['n_UserID'])
            # resolve hardways and remove the bet if lost
            # also resolving place bets
            if not comeout_roll:
                if dice_sum == 7:
                    winnings += row['i_dont'] * 2
                    if dice_sum == 4 or dice_sum == 10:
                        winnings += row['i_dont_odds'] + row['i_dont_odds'] * 1/2
                    elif dice_sum == 5 or dice_sum == 9:
                        winnings += row['i_dont_odds'] + row['i_dont_odds'] * 2/3
                    elif dice_sum == 6 or dice_sum == 8:
                        winnings += row['i_dont_odds'] + row['i_dont_odds'] * 5/6
                    user_id = row['n_UserID']
                    db.execute("DELETE FROM craps_board WHERE n_UserID=?", user_id)
                    db.execute("INSERT INTO craps_board (n_UserID) VALUES (?)", user_id)
                elif dice_sum == 4:
                    if die1 == 2 and die2 == 2:
                        winnings += row['i_hard_4'] * 8
                    db.execute("UPDATE craps_board SET i_hard_4 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_4'] * 9/5
                elif dice_sum == 5:
                    winnings += row['i_place_5'] * 7/5
                elif dice_sum == 6:
                    if die1 == 3 and die2 == 3:
                        winnings += row['i_hard_6'] * 10
                    db.execute("UPDATE craps_board SET i_hard_6 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_6'] * 7/6
                elif dice_sum == 8:
                    if die1 == 4 and die2 == 4:
                        winnings += row['i_hard_8'] * 10
                    db.execute("UPDATE craps_board SET i_hard_8 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_8'] * 7/6
                elif dice_sum == 9:
                    winnings += row['i_place_9'] * 7/5
                elif dice_sum == 10:
                    if die1 == 5 and die2 == 5:
                        winnings += row['i_hard_10'] * 8
                    db.execute("UPDATE craps_board SET i_hard_10 = ? WHERE n_UserID = ?", 0, row['n_UserID'])
                    winnings += row['i_place_10'] * 9/5
                if dice_sum == point:
                    winnings += row['i_pass']
                    if dice_sum == 4 or dice_sum == 10:
                        winnings += row['i_pass_odds'] + row['i_pass_odds'] * 2
                    elif dice_sum == 5 or dice_sum == 9:
                        winnings += row['i_pass_odds'] + row['i_pass_odds'] * 3/2
                    elif dice_sum == 6 or dice_sum == 8:
                        winnings += row['i_pass_odds'] + row['i_pass_odds'] * 6/5
                    db.execute("UPDATE craps_board SET i_dont=(?), i_pass_odds=(?), i_dont_odds=(?) "
                               "WHERE n_UserID = (?)", 0, 0, 0, row['n_UserID'])
                    
            if winnings > 0:
                balance = db.field("SELECT bankRoll FROM craps_bank WHERE UserID=?", row['n_UserID'])
                balance += winnings
                db.execute("UPDATE craps_bank SET bankRoll = ? WHERE UserID = ?", balance, row['n_UserID'])
                user = self.bot.get_user(row['n_UserID'])
                await ctx.send(f"""{user.name}\nWinnings: ${winnings:,.2f}\nCurrent bankroll: ${balance:,.2f}""")

        if comeout_roll:
            if dice_sum <= 3 or dice_sum == 7 or dice_sum >= 11:
                pass
            else:
                db.execute("UPDATE craps_current SET i_point = ? WHERE n_dummy = ?", dice_sum, MASTER_RECORD)
        elif dice_sum == point:
            db.execute("UPDATE craps_current SET i_point = ?, i_roll_nbr = ?"
                       " WHERE n_dummy = ?", 0, 0, MASTER_RECORD)
        elif dice_sum == 7:
            db.execute("UPDATE craps_current SET b_shooter = ?, i_point = ?, i_roll_nbr = ?"
                       " WHERE n_dummy = ?", 0, 0, 0, MASTER_RECORD)

    async def get_master_record(self, ctx):
        """returns control record `tuple` (point, shooter, current roll, discord user ID)"""
        row = db.record("SELECT * FROM craps_current WHERE n_dummy = ?", MASTER_RECORD)

        point = 0 if row['i_point'] is None else row['i_point']
        shooter = 0 if row['b_shooter'] is None else row['b_shooter']
        user = self.bot.get_user(shooter) if shooter != 0 else 0
        current_roll = 0 if row['i_roll_nbr'] is None else row['i_roll_nbr']
        return point, shooter, current_roll, user