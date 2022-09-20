from discord.ext import commands
import discord
import tickets
import territory_battles
import galactic_power
import squads
import mod_cog
import config
import new_help
import asyncio
import logging


intents = discord.Intents.default()
handler = logging.FileHandler(filename="bot.log", encoding='utf-8', mode='a')
discord.utils.setup_logging(handler=handler)
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("ready to go")


#@bot.event
#async def on_command_error(ctx: commands.Context, error):
#    print('here')
#    print(error)
#    if isinstance(error, commands.CommandNotFound):
#        await ctx.send("That is not a valid command. Try calling $help")
#        # args_list = str(error.args).split('"')
#        # called_command = args_list[1]
#        # for command in bot.all_commands:
#        raise error
#    elif isinstance(error, commands.errors.MissingRole):
#        if "'Officer'" in str(error):
#            await ctx.send("This command can only be called by an Officer")
#        else:
#            raise error
#    else:
#        print('here')
#        raise error

async def setup(bot):
    await bot.add_cog(tickets.Tickets(bot))
    await bot.add_cog(territory_battles.TB(bot))
    await bot.add_cog(galactic_power.Power(bot))
    #await bot.add_cog(squads.Squad(bot))
    #await bot.add_cog(mod_cog.ModPrinter(bot))
    #bot.remove_command('help')
    #await bot.add_cog(new_help.Help(bot))
    await bot.start(config.BOT_AUTH_CODE)

#bot.add_cog(tickets.Tickets(bot))
#bot.add_cog(territory_battles.TB(bot))
#bot.add_cog(galactic_power.Power(bot))
#bot.add_cog(squads.Squad(bot))
#bot.add_cog(mod_cog.ModPrinter(bot))
#bot.remove_command('help')
#bot.add_cog(new_help.Help(bot))

##################################################
asyncio.run(setup(bot))
