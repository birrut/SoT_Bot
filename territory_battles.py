import json
import requests
from requests.exceptions import Timeout
import os
import datetime
import time
import re
import discord
from discord.ext import commands, tasks
from asyncio import exceptions
import plotly.express as px
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np



class TB(commands.Cog):
    """Handles all the commands for reserving GP for TB deployment"""
    def __init__(self, bot):
        self.bot = bot
        print ('Territory battle cog initialized')

    #@bot.command(name="holding")

    def process_amount(self, amount, multiplier = None):
        """this is a helper function, it translates an amount with abbreviations into a number"""
        num_dict = {'m': 1000000, 'k': 1000, 'thousand': 1000, 'thou':1000, 'mil': 1000000, 'million': 1000000}
        try:
            number = float(amount)
        except ValueError:
            # This should happen if there is a letter in the input amount
            amount = amount.replace(',','')
            multiplier  = re.findall("[a-zA-Z]+", amount)
            number = float(re.findall("[0-9.]+", amount)[0])

        #process multiplier
        if multiplier:
            multiplier_number = num_dict[multiplier[0].casefold()]
        else:
            multiplier_number = 1
        #print (multiplier_number, ': ', type(multiplier_number))

        #print (number, ': ', type(number))

        output_amount = number * multiplier_number
        #print (output_amount)
            


        return int(output_amount)

    @commands.command(name="holding")
    async def holding(self, ctx):
        """Use this to reserve GP for TB deployment. 
        If you want to add for somebody else, use '$holding 123456 for member' """
        tb_file = 'data/tb' + str(ctx.message.guild.id) + ".json"
        message_word_list = ctx.message.content.split()
        #member = str(ctx.message.author).split('#')[0]
        member = str(ctx.message.author.display_name)
        if 'for' in message_word_list:
            ind_number = message_word_list.index('for')
            member = ctx.message.content.split('for ')[1]
            message_word_list = message_word_list[:ind_number]

        if len(message_word_list) > 2:
            out_number = self.process_amount(message_word_list[1], message_word_list[2:])
        else:
            out_number = self.process_amount(message_word_list[1])


        try:
            with open (tb_file, 'r') as in_data:
                old_data = json.loads(in_data.read())
        except FileNotFoundError:
            old_data = []



        write_out = {member : out_number}
        old_data.append(write_out)
        #print (old_data)



        with open(tb_file, 'w') as output:
            output.write(json.dumps(old_data))

        write_number = format (out_number, ',d')
        out_str = "Adding {} for member {}".format(write_number, member)
        await ctx.send(out_str)

    #@bot.command(name="list")
    @commands.command(name="list")
    async def list(self, ctx):
        """Lists all members who have reserved GP and the total."""
        total_list = []
        out_str = ''
        tb_file = 'data/tb' + str(ctx.message.guild.id) + ".json"
        message_word_list = ctx.message.content.split()
        with open (tb_file, 'r') as in_data:
            data = json.loads(in_data.read())

        for person in data:
            for name in person:
                total_list.append(person[name])
                out_str += "{}: {}\n".format(name, format(person[name], ',d'))

        total_number = format(sum(total_list), ',d')
        out_str += "Total reserved gp is {}".format(total_number)

        await ctx.send(out_str)
        print (sum(total_list))


    @commands.has_role("Officer")
    @commands.command(name="reset")
    async def reset(self, ctx):
        """Resets reserved GP. 
        Should be called after every TB phase, can only be called by members with the role Officer"""
        tb_file = 'data/tb' + str(ctx.message.guild.id) + ".json"

        data = []
        with open(tb_file, 'w') as out:
            out.write(json.dumps(data))

        out_message = "The reserved GP has been reest."
        await ctx.send(out_message)

    #@bot.command(name="remove")
    @commands.command(name="remove")
    async def remove(self, ctx):
        """Removes the reserved GP for this user.
        Or can be run for a different user with '$remove for user'"""
        out_list = []
        list_length = 0
        tb_file = 'data/tb' + str(ctx.message.guild.id) + ".json"
        message_word_list = ctx.message.content.split()
        #########################################
        #Test if we can use display name instead of author
        #print (ctx.message.author.display_name)
        member = str(ctx.message.author.display_name)
        lower_member = member.casefold()
        if 'for' in message_word_list:
            ind_number = message_word_list.index('for')
            member = ctx.message.content.split('for ')[1]
            lower_member = ctx.message.content.split('for ')[1].casefold()
            message_word_list = message_word_list[:ind_number]


        with open (tb_file, 'r') as in_data:
            data = json.loads(in_data.read())
            list_length = len(data)

        for person in data:
            for key in person:
                lower_person = key.casefold()
            print (person)
            #if member not in person:
            if lower_member != lower_person:
                out_list.append(person)
        new_length = len(out_list)
        with open(tb_file, 'w') as out_data:
            out_data.write(json.dumps(out_list))

        if new_length < list_length:
            await ctx.send("Removed {}'s reserved GP".format(member))
        else:
            await ctx.send("Couldn't find any held GP for {}.".format(member))
