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
class Meeting(commands.Cog, name="meeting"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.meetingChannelName = "current-meeting"
        self._meetingChannel: dict[int, discord.TextChannel] = {}
        self._stack: dict[int, list[discord.TextChannel]] = {}
        self._stackMessage: dict[int, discord.Message] = {}

    def meetingChannel(self, guild:discord.Guild) -> discord.TextChannel:
        """
        Gets a reference to the guild's meeting channel
        """
        if guild.id not in self._meetingChannel:
            self._meetingChannel[guild.id] = discord.utils.get(guild.channels, name="current-meeting")
        return self._meetingChannel[guild.id]
    
    def stackList(self, guild: discord.Guild) -> "list[str]":
        """
        Gets a reference to the guild's stack
        """
        if guild.id not in self._stack:
            self._stack[guild.id] = []
        return self._stack[guild.id]

    def stackMessage(self, guild: discord.Guild) -> discord.Message:
        """
        Gets a reference to the guild's stack
        """
        if guild.id not in self._stackMessage:
            self._stackMessage[guild.id] = None
        return self._stackMessage[guild.id]

    def setStackMessage(self, message: discord.Message):
        """
        Sets a reference for the guild's stack message
        """
        guild: discord.Guild = message.guild
        self._stackMessage[guild.id] = message

    def clearStackVars(self, guild: discord.Guild):
        """
        Clears out stack variables for the guild
        """
        self.stackList(guild).clear()
        self._stackMessage[guild.id] = None

    async def clearChannel(self, channel: discord.TextChannel):
        """
        Clears all messages out of a channel.
        """
        if channel is not None:
            async for msg in channel.history(limit=None):
                await msg.delete()

    async def printStack(self, guild: discord.Guild):
        """
        Prints out the current stack
        """
        msg = '\n'.join(f'{i} - {n.display_name}' for i, n in enumerate(self.stackList(guild)))
        embed = discord.Embed(
                title="Current Stack",
                description=msg,
                color=config.success
            )
        print(f"Message {self.stackMessage(guild)}")
        if self.stackMessage(guild) is None:
            self.setStackMessage(await self.meetingChannel(guild).send(embed=embed))
        else:
            await self.stackMessage(guild).edit(embed=embed)

    @commands.command(name="start-meeting")
    @commands.has_role("Approved")
    async def startMeeting(self, context: Context):
        """
        Starts a new meeting.
        """
        self.clearStackVars(context.guild)
        await self.clearChannel(self.meetingChannel(context.guild))
        await self.meetingChannel(context.guild).send("@everyone Meeting now starting.")
        await self.printStack(context.guild)  #Post Empty Stack

    @commands.command(name="stack")
    @commands.check_any(commands.has_role("Approved"), commands.has_role("Guest"))
    async def stack(self, context: Context):
        """
        Add yourself to the current stack.
        """
        await context.message.delete()
        self.stackList(context.guild).append(context.message.author)
        await self.printStack(context.guild)

    @commands.command(name="unstack")
    @commands.check_any(commands.has_role("Approved"), commands.has_role("Guest"))
    async def unstack(self, context: Context):
        """
        Remove yourself from the stack.
        """
        await context.message.delete()
        try:
            self.stackList(context.guild).remove(context.message.author)
        except ValueError:
            pass
        await self.printStack(context.guild)

    @commands.command(name="pop")
    @commands.has_role("Approved")
    async def pop(self, context: Context, n: int = 0):
        """
        Remove the numbered entry from the stack, defaults to the top entry.
        """
        await context.message.delete()
        if len(self.stackList(context.guild)) > n:
            self.stackList(context.guild).pop(n)
            await self.printStack(context.guild)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Meeting(bot))