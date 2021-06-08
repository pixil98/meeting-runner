import os, sys, discord
from discord.ext import commands
from discord.ext.commands.context import Context

# Only if you want to use variables that are in the config.py file.
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

# Here we name the cog and create a new class for the cog.
class Meeting(commands.Cog, name="meeting"):

    def __init__(self, bot):
        self.bot = bot
        self.initEmptyVars()
    
    def initEmptyVars(self):
        # Meeting vars
        self.meetingRunning = False
        self.meetingChannel: discord.TextChannel = None

        # Stack vars
        self.stackList = []
        self.stackMsg = None

        # Agenda vars
        self.angendaList = []
        self.nextAgendaList = []

    @commands.command(name="start-meeting")
    async def startMeeting(self, context: Context):
        """
        Starts a new meeting.
        """
        if self.meetingRunning == True:
            return

        self.meetingRunning = True
        self.meetingChannel = discord.utils.get(context.guild.channels, name="current-meeting")
        #await self.meetingChannel.send("@everyone Meeting now starting.")

        #Post Agenda here
        #agenda = discord.Embed(
        #        title="Agenda",
        #        description="This is where the agenda would be",
        #        color=config.success
        #)
        #await self.meetingChannel.send(embed=agenda)

        #Post Empty Stack
        await self.printStack()

    
    @commands.command(name="end-meeting")
    async def endMeeting(self, context: Context):
        """
        Ends the current meeting.
        """
        if self.meetingRunning == False:
            return

        #await self.meetingChannel.delete()
        self.initEmptyVars()

    @commands.command(name="stack")
    async def stack(self, context: Context):
        """
        Add yourself to the current stack.
        """
        await context.message.delete()
        if self.meetingRunning == False:
            return

        self.stackList.append(context.message.author)
        await self.printStack()

    @commands.command(name="unstack")
    async def unstack(self, context: Context):
        """
        Remove yourself from the stack.
        """
        await context.message.delete()
        if self.meetingRunning == False:
            return

        try:
            self.stackList.remove(context.message.author)
        except ValueError:
            pass
        await self.printStack()

    @commands.command(name="pop")
    async def pop(self, context: Context, n: int = 0):
        """
        Remove the numbered entry from the stack, defaults to the top entry.
        """
        await context.message.delete()
        if len(self.stackList) > n:
            self.stackList.pop(n)
            await self.printStack()

    async def printStack(self):
        msg = '\n'.join(f'{i} - {n.display_name}' for i, n in enumerate(self.stackList))
        embed = discord.Embed(
                title="Current Stack",
                description=msg,
                color=config.success
            )

        if self.stackMsg is None:
            self.stackMsg = await self.meetingChannel.send(embed=embed)
        else:
            await self.stackMsg.edit(embed=embed)
    
    @commands.command(name="agenda-add")
    async def agendaAdd(self, context: Context):
        pass

    @commands.command(name="debug")
    async def debug(self, context: Context):
        await context.send(vars(self))
    

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Meeting(bot))