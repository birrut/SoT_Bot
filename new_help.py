import discord
from discord.ext import commands
from discord.errors import Forbidden
import config

"""
You must put "bot.remove_command('help')" in your bot,
and the command must be in a cog for it to work.
"""


async def send_embed(ctx, embed):

    image = discord.File('bot.png', filename='bot.png')
    embed.set_thumbnail(url='attachment://bot.png')
    try:
        await ctx.send(file=image, embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):
        """Shows all modules of that bot"""
        prefix = "$"
        version = config.BOT_VERSION
        found = False
        # setting owner name - if you don't wanna be mentioned remove line 49-60 and adjust help text (line 88)
        owner = "Chirrut"       # ENTER YOU DISCORD-ID
        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:
            # checks if owner is on this server - used to 'tag' owner
            try:
                owner = ctx.guild.get_member(owner).mention

            except AttributeError:
                owner = owner

            # starting to build embed
            emb = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                description=f'Use `{prefix}help <module>` to gain more information about that module '
                                            f':smiley:\n')
            found = True
            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.bot.cogs:
                # print (dir(self.bot.cogs[cog]))
                commands = self.bot.cogs[cog].walk_commands()
                cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'
                for command in commands:
                    cogs_desc += f"`{prefix}{command}` "
                cogs_desc += '\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Modules', value=cogs_desc, inline=False)
            found = True

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'
                # elif not command.hidden:
                #    commands_desc += f'{command.name}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

            # setting information about author
            # emb.add_field(name="About", value=f"The Bots is developed by Chriѕ#0001, based on discord.py.\n\
            #                        This version of it is maintained by {owner}\n\
            #                        Please visit https://github.com/nonchris/discord-fury to submit ideas or bugs.")
            emb.set_footer(text=f"Bot is running {version}")

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:
            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.green())
                    found = True
                    try:
                        for command in self.bot.cogs[cog].walk_commands():
                            emb.add_field(name=f"`{prefix}{command}`", value=command.help, inline=False)
                    except AttributeError:
                        pass
                    # getting commands from cog
                    # for command in self.bot.get_cog(cog).get_commands():
                        # print (dir(command))
                        # if cog is not hidden
                        # if not command.hidden:
                        #    emb.add_field(name=f"`{prefix}{command.name}`", value=command.help, inline=False)
                        #    c_list = get_subs(command)
                        #        emb.add_field(name=f"`{prefix}{command} {other.name}`", value=other.help, inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                for command in self.bot.commands:
                    if command.name.lower() == input[0].lower():
                        emb = discord.Embed(title=f"{command.name}", description=command.help, color=discord.Color.blue())
                        found = True
                        break
                else:
                    emb = discord.Embed(title="What's that?!",
                                        description=f"I've never heard from a module called `{input[0]}` before :scream:",
                                        color=discord.Color.orange())
                    found = True

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            arg = ' '.join(input)
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():
                    for command in self.bot.cogs[cog].walk_commands():
                        if str(command).lower() == arg.lower():
                            emb = discord.Embed(title=f"{command}", description=command.help, color=discord.Color.blue())
                            found = True
                            break

        if not found:
            emb = discord.Embed(title="I don't know.",
                                description=f"I don't know about `{prefix}{arg}`. Try calling `{prefix}help` :sweat_smile:",
                                color=discord.Color.orange())

        await send_embed(ctx, emb)
