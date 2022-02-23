from datetime import datetime
from typing import Optional
from discord import Member, Embed
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure, MissingPermissions
from discord.ext.commands import command, has_permissions, bot_has_permissions


# help menu main class.  We control the look and feel of the pages as they show.
class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="shutdown")
    @has_permissions(kick_members=True)
    async def shutdown(self, ctx):
        await self.bot.close()

    @shutdown.error
    async def shutdown_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="kick")
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick_member(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided"):
        if not len(targets):
            await ctx.send("One of more required arguments are missing.")
        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position and not
                target.guild_permissions.administrator):
                    await target.ban(reason=reason)

                    embed = Embed(title="Member kicked",
                                  color=0xDD2222,
                                  timestamp=datetime.utcnow())
                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
                              ("Actioned by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline= inline)

                    await self.log_channel.send(embed=embed)
                else:
                    await ctx.send(f"{target.display_name} could not be kicked.")

            await ctx.send("Action Completed.")

    @kick_member.error
    async def kick_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @command(name="ban")
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban_member(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided"):
        if not len(targets):
            await ctx.send("One of more required arguments are missing.")
        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_role.position and not
                    target.guild_permissions.administrator):
                    await target.ban(reason=reason)

                    embed = Embed(title="Member banned",
                                  color=0xDD2222,
                                  timestamp=datetime.utcnow())
                    embed.set_thumbnail(url=target.avatar_url)

                    fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
                              ("Actioned by", ctx.author.display_name, False),
                              ("Reason", reason, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline= inline)

                    await self.log_channel.send(embed=embed)
                else:
                    await ctx.send(f"{target.display_name} could not be kicked.")

            await ctx.send("Action Completed.")

    @ban_member.error
    async def ban_members_error(self, ctx, exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Insufficient permissions to perform that task.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.log_channel = self.bot.get_channel(941827777336836116)
            self.bot.cogs_ready.ready_up("mod")


def setup(bot):
    bot.add_cog(Mod(bot))
