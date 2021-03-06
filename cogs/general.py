import os, sys, discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.context import Context

# Only if you want to use variables that are in the config.py file.
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

# Here we name the cog and create a new class for the cog.
class General(commands.Cog, name="general"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @commands.command(name="approve")
    @commands.has_role("Approved")
    async def approve(self, context: Context, user: discord.Member = None):
        """
        Approve a user to have access to the discord.
        """
        role = discord.utils.get(user.guild.roles, name="Approved")
        await user.add_roles(role, reason=f"Approved by {context.message.author}")

    @approve.error
    async def approve_error(self, context: Context, error):
        if isinstance(error, discord.ext.commands.MemberNotFound):
            await context.send(error)

    @commands.command(name="invite")
    @commands.has_role("Approved")
    async def invite(self, context: Context):
        """
        Generate a single use invite that is valid for 7 days.
        """
        inv: discord.Invite = await context.channel.create_invite(max_age = 604800, max_uses = 1, reason = f"Requested by {context.message.author}")
    
        await context.author.send(inv.url)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(General(bot))