from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    # this allows changing of the prefix from + to a custom one.  It is loaded from the database.db file
    @command(name="prefix")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):
        if len(new) > 5:
            await ctx.send("The prefix cannot be more than 5 characters in length.")
        else:
            # this command references the guilds table in the build.sql file, the Prefix field, when the GuildId
            # field matches the passed argument
            db.execute("UPDATE guilds SET Prefix = ? WHERE GuildId = ?", new, ctx.guild.id)
            await ctx.send(f"Prefix set to {new}")

    @change_prefix.error
    async def change_prefix_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("You need the Manage Messages permission to do that.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))
