import os, sys, discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.context import Context
import datetime

# Only if you want to use variables that are in the config.py file.
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

FOLLOWUP_LOOKBACK_DAYS = 7
FOLLOWUP_TITLE = "**Follow-ups**"
CHECK_MARK_EMOJI = u"\u2705"
BULLET_POINT = u"\u2022"

# Here we name the cog and create a new class for the cog.
class Meeting(commands.Cog, name="meeting"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.meetingChannelName = "current-meeting"
        self._meetingChannel: dict[int, discord.TextChannel] = {}
        self._stack: dict[int, list[discord.TextChannel]] = {}
        self._stackMessage: dict[int, discord.Message] = {}
        self._followUpChannel: dict[int, discord.TextChannel] = {}
        self._followUps: dict[int, list[discord.Message]] = {}

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

    def followUpChannel(self, guild: discord.Guild) -> discord.TextChannel:
        """
        Gets a reference to the guild's channel for followups
        """
        if guild.id not in self._followUpChannel:
            self._followUpChannel[guild.id] = discord.utils.get(guild.channels, name="agenda-and-followups")
        return self._followUpChannel[guild.id]

    def followUps(self, guild: discord.Guild):
        """
        gets a reference to the guild's followups
        """
        if guild.id not in self._followUps:
            self._followUps[guild.id] = []
        return self._followUps[guild.id]

    async def addFollowUp(self, guild: discord.Guild,  message: discord.Message):
        """
        Adds a followup message to the current list of followups
        """
        if len(message.mentions) > 0 or message.mention_everyone:
            self.followUps(guild).append(message)
        else:
            await message.channel.send("Error: follow-ups need an owner! Tag someone in your command.")

    def clearFollowUps(self, guild: discord.Guild):
        """
        Clears the current list of followups
        """
        self.followUps(guild).clear()

    async def printFollowUps(self, guild: discord.Guild):
        """
        Sends a summary of the followups as a message
        """
        if len(self.followUps(guild)) == 0:
            return

        text = FOLLOWUP_TITLE + '\n' + \
            '\n'.join(BULLET_POINT + followUp.content.replace(BULLET_POINT, "").replace("!follow-up", "")
                      for followUp in self.followUps(guild))
        caption = "React with the check mark when you've completed all of your follow-ups."
        embed = discord.Embed(
                title=FOLLOWUP_TITLE,
                description=text,
                color=config.success
            )
        self.clearFollowUps(guild)
        message = await self.followUpChannel(guild).send(content=text)
        await message.add_reaction(CHECK_MARK_EMOJI)

    async def membersToRemind(self, followUpChannel: discord.TextChannel) -> list[discord.Member]:
        """
        Looks up the members that need reminding from recent meetings.
        """
        members = []
        startDateTime = datetime.datetime.utcnow() - datetime.timedelta(days=FOLLOWUP_LOOKBACK_DAYS)
        async for message in followUpChannel.history(limit=None, after=startDateTime):
            if message.author != self.bot.user: continue
            if message.content[:len(FOLLOWUP_TITLE)] != FOLLOWUP_TITLE: continue
            doneUsers = []
            for reaction in message.reactions:
                if reaction.emoji == CHECK_MARK_EMOJI:
                    doneUsers = await reaction.users().flatten()
            for member in message.mentions:
                if (member not in doneUsers) and (member not in members):
                    members.append(member)
        return members

    async def sendFollowUpReminders(self, members: list[discord.Member]):
        """
        Sends a DM to the users in the list
        """
        for member in members:
            await member.send(
                content="Don't forget to complete your follow-ups in the #agenda-and-followups channel!. " +
                        "If you're done, react with the check mark to suppress future reminders.")

    async def remindFollowUps(self, guild: discord.Guild):
        """
        Sends DM reminders to everyone who hasn't completed their follow-ups from
        any meeting in the last week.
        """
        membersToRemind = await self.membersToRemind(self.followUpChannel(guild))
        await self.sendFollowUpReminders(membersToRemind)

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

    @commands.command(name="end-meeting")
    @commands.has_role("Approved")
    async def endMeeting(self, context: Context):
        """
        Ends a meeting.
        """
        await self.printFollowUps(context.guild)

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

    @commands.command(name="follow-up")
    @commands.has_role("Approved")
    async def followUp(self, context: Context):
        """
        Assign somebody a follow-up by tagging them
        """
        await self.addFollowUp(context.guild, context.message)

    @commands.command(name="test-reminders")
    @commands.has_role("Approved")
    async def testReminders(self, context: Context):
        """
        Test the follow-up reminders feature
        """
        await self.remindFollowUps(context.guild)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Meeting(bot))