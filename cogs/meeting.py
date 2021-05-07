import os, sys, discord
from discord.ext import commands

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
        self.meetingChannel = None

        # Stack vars
        self.stackList = []
        self.stackMsg = None

        # Agenda vars
        self.angendaList = []
        self.nextAgendaList = []

    @commands.command(name="start-meeting")
    async def startMeeting(self, context):
        """
        Starts a meeting.
        """
        if self.meetingRunning == True:
            return

        self.meetingRunning = True
        self.meetingChannel = await context.guild.create_text_channel(name="current meeting")

        await self.meetingChannel.send("@everyone Meeting now starting.")

        #Post Agenda here
        agenda = discord.Embed(
                title="Agenda",
                description="This is where the agenda would be",
                color=config.success
        )
        await self.meetingChannel.send(embed=agenda)

        #Post Empty Stack
        await self.printStack()

    
    @commands.command(name="end-meeting")
    async def endMeeting(self, context):
        """
        Ends the current meeting.
        """
        if self.meetingRunning == False:
            return

        await self.meetingChannel.delete()
        self.initEmptyVars()


    @commands.command(name="stack")
    async def stack(self, context):
        """
        Add yourself to the current stack.
        """
        await context.message.delete()
        if self.meetingRunning == False:
            return

        self.stackList.append(context.message.author.name)
        await self.printStack()

    @commands.command(name="unstack")
    async def unstack(self, context):
        """
        Remove yourself from the stack.
        """
        await context.message.delete()
        if self.meetingRunning == False:
            return

        try:
            self.stackList.remove(context.message.author.name)
        except ValueError:
            pass
        await self.printStack()

    @commands.command(name="pop")
    async def pop(self, context):
        """
        Remove the top entry from the stack.
        """
        await context.message.delete()
        if len(self.stackList) > 0:
            self.stackList.pop(0)
            await self.printStack()

    async def printStack(self):
        msg = '\n'.join(f'{i} - {n}' for i, n in enumerate(self.stackList))
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
    async def agendaAdd(self, context):
        pass

    @commands.command(name="debug")
    async def debug(self, context):
        await context.send(vars(self))
    

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Meeting(bot))