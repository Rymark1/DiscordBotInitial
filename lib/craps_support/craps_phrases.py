from random import choice
from lib.db import db


class CrapsPhrases:
    craps_channel = 946091566433456128

    async def choose_phrase(self, ctx, die1, die2):
        point = db.field("SELECT i_point FROM craps_current WHERE n_dummy=?", 1)
        comeout_roll = True if point == 0 else False

        sum_of_dice = die1 + die2
        two_phrases = ["Craps", "eye balls", "two aces", "rats eyes", "snake eyes", "push the don’t",
                       "eleven in a shoe store", "twice in the rice", "two craps two two bad boys from Illinois",
                       "two crap aces", "aces in both places", "a spot and a dot", "dimples."]
        three_phrases = ["Craps", "ace-deuce", "three craps ace caught a deuce no use", "divorce roll come up single",
                         "winner on the dark side", "three craps three the indicator",
                         "crap and a half flip side ‘O Yo",
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
                            "Benny Blue you’re all through", "three-four now we’re poor",
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
                                                                                        "Screw the donts",
                              "Take the darkside"]
        eleven_front_winner = ["Eleven Front Line Winner", "Take the Donts Pay the Line", "Yo that front line"]

        four_hard = ["four the hard way", "two spots and two dots.", "hit us in the tu tu", "Double deuce"]
        six_hard = ["six the hard way", "pair-o-treys waiter’s roll", "Brooklyn Forest",
                    "watch the Rhineland, its thirty-three"]
        eight_hard = ["eight the hard way", "the windows", "A square pair like mom and dad"]
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
