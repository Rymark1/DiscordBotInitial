from random import choice
from lib.db import db
import asyncio

MASTER_RECORD = 1


class CrapsPhrases:
    craps_channel = 946091566433456128

    async def choose_phrase(self, ctx, die1, die2):
        board_list = await asyncio.gather(CrapsPhrases.get_master_record(self, ctx))
        point, shooter, current_roll, user = board_list[0]

        comeout_roll = (point == 0)

        dice_sum = die1 + die2

        # Someday I'll stop being lazy and make a database for these.  Then it'll be easier to load and use the dict
        phrases = {
            'm7_front_winner': ["Seven Front Line Winner", "Take the Donts Pay the Line", "Big Red saves the day"
                                                                                          "Screw the donts",
                                "Take the darkside"],
            'm11_front_winner': ["Eleven Front Line Winner", "Take the Donts Pay the Line", "Yo that front line"],
            'm3_phrases': ["Craps", "ace-deuce", "three craps ace caught a deuce no use", "divorce roll come up single",
                           "winner on the dark side", "three craps three the indicator",
                           "crap and a half flip side ‘O Yo",
                           "small ace deuce can’t produce", "the other side of eleven’s tummy",
                           "three craps the middle",
                           "two-one son of a gun."],
            'm4_phrases': ["Little Joe", "little Joe from Kokomo", "ace trey the easy way"],
            'm5_phrases': ["After five the field’s alive", "little Phoebe", "fiver fiver racetrack driver",
                           "we got the fever", "five fever", "five no field five."],
            'm6_phrases': ["Big Red catch’em in the corner", "like a blue chip stock", "the national average",
                           "sixie from Dixie."],
            'm8_phrases': ["Ozzie and Harriet", "Donnie and Marie", "eighter from Decatur.", "eight is great"],
            'm9_phrases': ["Center field", "center of the garden", "ocean liner niner", "Nina from Pasadena",
                           "Nina Niner wine and dine her"],
            'm10_phrases': ["the big one on the end", "sixty-four out the door.", "I got a 10er for you",
                            "fourty-six drops like the iron curtain"],
            'm11_phrases': ["Yo leven", "yo levine the dancing queen", "six five no jive",
                            "it’s not my eleven it’s yo eleven."],
            'm_1_6_phrases': ["Seven out line away", "grab the money", "seven’s a bruiser the front line’s a loser",
                              "Benny Blue you’re all through", "six-ace you lost the race", "Six-ace in your face",
                              "six ace end of the race", "six one you’re all done", "up pops the devil"],
            'm_2_5_phrases': ["Seven out line away", "grab the money", "seven’s a bruiser the front line’s a loser",
                              "Benny Blue you’re all through", "up pops the devil", "five two you’re all through"],
            'm_3_4_phrases': ["Seven out line away", "grab the money", "seven’s a bruiser the front line’s a loser",
                              "Benny Blue you’re all through", "three-four now we’re poor",
                              "three-four we’ve lost the war.", "up pops the devil", "four-three woe is me"],
            'm_4_5_phrases': ["Center field", "center of the garden", "ocean liner niner", "Nina from Pasadena",
                              "Nina Niner wine and dine her", "What shot Jesse James? A forty-five."],
            'm2_hard': ["Craps", "eye balls", "two aces", "rats eyes", "snake eyes", "push the don’t",
                        "eleven in a shoe store", "twice in the rice", "two craps two two bad boys from Illinois",
                        "two crap aces", "aces in both places", "a spot and a dot", "dimples."],
            'm4_hard': ["four the hard way", "two spots and two dots.", "hit us in the tu tu", "Double deuce"],
            'm6_hard': ["six the hard way", "pair-o-treys waiter’s roll", "Brooklyn Forest",
                        "watch the Rhineland, its thirty-three"],
            'm8_hard': ["eight the hard way", "the windows", "A square pair like mom and dad"],
            'm10_hard': ["ten the hard way", "Puppy paws", "pair-a-roses", "pair of sunflowers",
                         "fifty-five to stay alive",
                         "two stars from mars"],
            'm12_hard': ["Craps", "boxcars", "atomic craps", "a whole lot of crap", "craps to the max",
                         "12 craps it’s crap unless you’re betting on it", "all the spots we got",
                         "all the spots and all the dots", "all the crap there is", "outstanding in your field",
                         "triple dipple in the lucky ducky", "midnight", "double saw on boxcars", "Crapus Maximus."]
        }

        # generic names, and override if we need special phrases.
        name_of_list = "m" + str(dice_sum) + "_"
        if die1 == die2:
            name_of_list += "hard"
        else:
            name_of_list += "phrases"

        if (dice_sum == 7 or dice_sum == 11) and comeout_roll:
            name_of_list = "m" + str(dice_sum) + "_front_winner"
        elif dice_sum == 7:
            if die1 == 1 or die2 == 1:
                name_of_list = "m_1_6_phrases"
            elif die1 == 2 or die2 == 2:
                name_of_list = "m_2_5_phrases"
            elif die1 == 3 or die2 == 3:
                name_of_list = "m_3_4_phrases"
        elif dice_sum == 9:
            if die1 == 4 or die2 == 4:
                name_of_list = "m_4_5_phrases"

        return choice(phrases[name_of_list])

    async def send_outcome_message(self, ctx, die1, die2):
        board_list = await asyncio.gather(CrapsPhrases.get_master_record(self, ctx))
        point, shooter, current_roll, user = board_list[0]
        comeout_roll = (point == 0)
        dice_sum = die1 + die2

        come_out_win_phrases = ["front line winner back line skinner", "Winner Winner, pay the line", "pay that line"]
        come_out_lose_phrases = ["Craps, front line loser", "Pay the Don'ts", "The Dark side wins this roll"]
        point_hits = ["Point hit, hot shooter", "Pay the front line, thats a winner",
                      "Won't someone think of the Casinos profits."]
        big_red = ["Shooter out", "Better luck next round", "Pay the donts"]

        if comeout_roll:
            if dice_sum <= 3 or dice_sum == 12:
                await ctx.send(choice(come_out_lose_phrases))
            elif dice_sum == 7 or dice_sum == 11:
                await ctx.send(choice(come_out_win_phrases))
        elif dice_sum == 7:
            await ctx.send(choice(big_red))
        elif point == dice_sum:
            await ctx.send(choice(point_hits))
            await ctx.send("All pass-line bets are still riding. All other bets are off for the come-out roll.")

    async def get_master_record(self, ctx):
        """returns control record `tuple` (point, shooter, current roll, discord user ID)"""
        row = db.record("SELECT * FROM craps_current WHERE n_dummy = ?", MASTER_RECORD)

        point = 0 if row['i_point'] is None else row['i_point']
        shooter = 0 if row['b_shooter'] is None else row['b_shooter']
        user = self.bot.get_user(shooter) if shooter != 0 else 0
        current_roll = 0 if row['i_roll_nbr'] is None else row['i_roll_nbr']
        return point, shooter, current_roll, user
