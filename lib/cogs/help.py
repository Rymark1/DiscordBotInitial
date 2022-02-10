from asyncio import sleep
from typing import Optional

from discord import Embed
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog
from discord.ext.commands import command


# function to have the output line show the command|aliases, then required arguments
# in <> and optional in <>
# then returns the created items
def syntax(cmd):
    cmd_and_aliases = "|".join([str(cmd), *cmd.aliases])
    params = []

    for key, value in cmd.params.items():
        if key not in ("self", "ctx"):
            # ternary operator.  syntax is (true expression) if (condition) else (false expression)
            params.append(f"[{key}]" if 'Optional' in str(value) else f"<{key}>")
    params = " ".join(params)

    return f"'{cmd_and_aliases} {params}'"


# help menu main class.  We control the look and feel of the pages as they show.
class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        # determins number of items per page
        super().__init__(data, per_page=3)

    # sets up how the box looks on the screen.
    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(title="Help",
                      description="Welcome to the Botty help dialog!",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} commands.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, page):
        fields = []

        for entry in page:
            fields.append((entry.brief or "No Description", syntax(entry)))

        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"Help with `{command}`",
                      description=syntax(command),
                      colour=ctx.author.colour)
        embed.add_field(name="Command description", value=command.help)
        await ctx.send(embed=embed)

    @command(name="help", brief="Halp")
    async def show_help(self, ctx, cmd: Optional[str]):
        """Shows this message."""
        # to give the message time to process and load fully
        await sleep(1)
        await ctx.message.delete()
        if cmd is None:
            menu = MenuPages(source=HelpMenu(ctx, list(self.bot.commands)),
                             delete_message_after=True,
                             timeout=60.0)
            await menu.start(ctx)

        else:
            if command := get(self.bot.commands, name=cmd):
                await self.cmd_help(ctx, command)

            else:
                await ctx.send("That command does not exist.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("help")


def setup(bot):
    bot.add_cog(Help(bot))
