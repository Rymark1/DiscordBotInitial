from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound
from discord.ext.commands import Context

# Importing my database
from ..db import db

# customizable prefix
PREFIX = "+"

# my personal ID on steam.  Can be found by enabling developer options and right clicking a name.
OWNER_IDS = [263423150346338304]

# reference to where all the COGS are, or in this case, commands for the bot
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]


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


# the actual class of the bot.
class Bot(BotBase):
    # initial startup where variables get set and paths get defined
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

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

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        else:
            raise exc

    # This is where the bot box and the image appear on load-up.  Happens once the bot is running.
    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(939559318787858433)
            self.stdout = self.get_channel(939559318787858436)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()

            embed = Embed(title="Now online!", description="Botty is now online.",
                          colour=0xFF0000, timestamp=datetime.utcnow())
            fields = [("Name", "Value", True),
                      ("Another field", "This field is next to the other one.", True),
                      ("A non-inline field", "This field will appear on it's own row.", False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_author(name="Ryan's Bot", icon_url=self.guild.icon_url)
            embed.set_footer(text="This is a footer!")
            await self.stdout.send(embed=embed)

            await self.stdout.send(file=File("./data/images/profile.png"))

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
