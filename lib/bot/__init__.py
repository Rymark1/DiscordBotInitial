from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, Intents
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions

# Importing my database
from ..db import db

# # customizable prefix
# PREFIX = "+"

# my personal ID on steam.  Can be found by enabling developer options and right clicking a name.
OWNER_IDS = [263423150346338304]

# reference to where all the COGS are, or in this case, commands for the bot
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]

IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

# this is a class to check and make sure the cogs are ready for use
class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM Guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


# the actual class of the bot.
class Bot(BotBase):
    # initial startup where variables get set and paths get defined
    def __init__(self):
        # # this is the setting of the prefix
        # self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        # changing this from command_prefix=PREFIX to
        # command_prefix=get_prefix
        super().__init__(command_prefix=get_prefix,
                         owner_ids=OWNER_IDS,
                         intents=Intents.all())

    # initial startup of Cogs
    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("setup complete")

    # starting the bot
    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        # this references the token file from Discord for the bot.  Don't share unless you want someone to control the bot
        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send("I'm not ready to receive commands.  Please wait a few seconds.")

    async def rules_reminder(self):
        await self.stdout.send("Remember to adhere to the rules!")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        await self.stdout.send("An error occurred.")
        raise

    # on errors occurring, this spits out the messages "something went wrong" and "An error occurred"
    # By adding in the BadArguement or CommandNotFound, we are preventing the extra messages from displaying.
    # The HTTPException will throw if the message can't send
    # The Forbidden instance is for when the bot tries to do something it doesn't have permissions for
    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("1 or more required arguments are missing")
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"Please wait.  The command is cooling off for {exc.retry_after:,.2f} seconds. "
                           f"{str(exc.cooldown.type).split('.')[-1]} cooldown.")
        elif hasattr(exc, "original"):
            # if isinstance(exc, HTTPException):
            # await ctx.send("Unable to send message.")
            if isinstance(exc.original, Forbidden):
                await ctx.send("I don't have permission for that")
            else:
                raise exc.original
        else:
            raise exc
    # could also make and use the list defined above.
    # if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS])
    #   pass (or whatever code you want for all those specific exceptions.


    # This is where the bot box and the image appear on load-up.  Happens once the bot is running.
    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(939559318787858433)
            self.stdout = self.get_channel(939559318787858436)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()

            # commenting out the inital embed until I can put useful information.
            # embed = Embed(title="Now online!", description="Botty is now online.",
            #               colour=0xFF0000, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True),
            #           ("Another field", "This field is next to the other one.", True),
            #           ("A non-inline field", "This field will appear on it's own row.", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Ryan's Bot", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is a footer!")
            # await self.stdout.send(embed=embed)

            # commenting out the pigeon
            # await self.stdout.send(file=File("./data/images/profile.png"))

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("Now online!")
            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
