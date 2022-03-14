import asyncio
from datetime import datetime

from _sqlite3 import Error
from discord import Embed, File
from discord.ext.commands import Cog, command, cooldown, has_permissions, CheckFailure, BucketType
from random import randint

from lib.craps_support.crap_resolve import CrapsResolve
from lib.craps_support.craps_phrases import CrapsPhrases
from ..db import db


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
        shooter_id = randint(0, len(shooters) - 1)
        db.execute("UPDATE craps_current SET b_shooter = ? WHERE n_dummy = ?", shooters[shooter_id], 1)
        user = self.bot.get_user(shooters[shooter_id])
        await ctx.send("The shooter is " + user.name)

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

        # embedding image to return dice roll
        die_roll_url = f"{str(die1)}{str(die2)}.png"
        embed = Embed(title=f"Roll {die_roll}",
                      colour=0xFF0000,
                      timestamp=datetime.utcnow())

        file = File(f"./data/images/{die_roll_url}", filename="image.png")
        embed.set_image(url="attachment://image.png")
        phrase, = await asyncio.gather((CrapsPhrases.choose_phrase(self, ctx, die1, die2)))
        embed.set_footer(text=phrase)
        await ctx.send(file=file, embed=embed)
        await asyncio.gather((CrapsPhrases.send_outcome_message(self, ctx, die1, die2)))

        await asyncio.gather((CrapsResolve.resolve_bets(self, ctx, die1, die2)))

    @command(name="bets")
    async def print_current_board(self, ctx):
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

    @command(name="status")
    async def status(self, ctx):
        # only work in craps channel
        if ctx.channel.id != self.craps_channel.id:
            return
        row = db.record("SELECT * FROM craps_current WHERE n_dummy = ?", 1)
        if row is None:
            return

        if row['b_shooter'] is None or row['b_shooter'] == 0:
            await ctx.send(f"Current point: {row['i_point']}\tCurrent shooter: N/A\tCurrent roll: {row['i_roll_nbr']}")
        else:
            user = self.bot.get_user(row['b_shooter'])
            await ctx.send(f"Current point: {row['i_point']}\tCurrent shooter: {user.name}\tCurrent roll:"
                           f" {row['i_roll_nbr']}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.craps_channel = self.bot.get_channel(946091566433456128)
            self.bot.cogs_ready.ready_up("craps")


def setup(bot):
    bot.add_cog(Craps(bot))
