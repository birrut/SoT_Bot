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
import helper




class Power(commands.Cog):
    """Handles all the commands related to gp"""
    def __init__(self, bot):
        self.bot = bot
        self.test = False
        #At some point, this should be in a config file do I need this in this class?
        self.server_list = ['884464695476625428', '888611226593136690']
        self.server_data_list = []
        for server in self.server_list:
            self.server_data = {}
            self.server_data['server'] = server
            #self.server_data['last_saved_time'] = self.get_last_saved_time(server)
            if server == '888611226593136690':
                self.server_data['channel'] = '888611287112749106'
            elif server == '884464695476625428':
                self.server_data['channel'] = '888234595269619772'

            self.server_data_list.append(self.server_data)

        print ('Power cog initialized')

    def get_proper_name(self, name, dic_list):
        """takes a name from command and a one days list of dictionaries of form {id:[name, tickets]} and returns id."""

        out_list = []
        for key in dic_list:
            #print (dic_list[key])
            try:
                if dic_list[key][0].casefold()==name.casefold():
                    out_list.append((key, dic_list[key][0]))
                    return [key, dic_list[key][0]]
            except TypeError:
                pass
        if not out_list:
            for key in dic_list:
                try:
                    if name.casefold() in dic_list[key][0].casefold():
                        out_list.append((key, dic_list[key][0]))
                except TypeError:
                    pass
        if len(out_list) == 1:
                return out_list[0]


    def total_format(self, number):
        f_list = ['', 'k', 'm']
        mag = 0
        sign =  ''
        if number < 0:
            sign = '-'
            number = abs(number)
        while number > 1000:
            mag +=1
            number = number / 1000


        return "{}{}{}".format(sign, round(number), f_list[mag])



    @commands.group(invoke_without_command=True)
    async def power(self, ctx, days=7):
        """Master command for Galactic Power. 
        If called alone, gives history of gp. """
        #{player: gp}
        #player_gp_list = []
        total_gp = []
        out_str = ''
        gp_list = []
        date_list = []
        try:
            day_number = int(days) + 1
        except ValueError:
            day_number = 31
        file_name = 'data/' + str(ctx.message.guild.id) + 'guild_data.json'
        with open(file_name, 'r') as guild_file:
            guild_data = json.loads(guild_file.read())

        print (len(guild_data))
        if len(guild_data) < day_number -1:
            day_number = len(guild_data)

        for day in guild_data[-day_number:]:
            date = datetime.datetime.fromisoformat(day['date'])
            date_list.append(date)
            gp_list.append(day['profile']['guildGalacticPower'])
            gp = format(day['profile']['guildGalacticPower'], ',d')
            out_str += "{}: {}\n".format(date.date(), gp)
            day_dict = {date: gp}
            total_gp.append(day_dict)

        growth_list = helper.get_growth_list(gp_list)
        #growth_list.insert(0,0)
        date_list.pop(0)
        gp_list.pop(0)
        out_str = ''
        multiple = False
        str_list = []
        for ite in range(len(date_list)):
            out_str += "{}-{}: {} Growth: {}.\n".format(date_list[ite].month, date_list[ite].day, format(gp_list[ite], ',d'), format(growth_list[ite], ',d'))
            if len(out_str) >= 1900:
                multiple = True
                first_str = out_str
                out_str = ''
                str_list.append(first_str)


        out_str += "Total growth over the last {} days: {}.\n".format(len(growth_list), format(sum(growth_list), ',d'))
        out_str += f"Average daily growth: {format(round(sum(growth_list)/len(growth_list)), ',d')}"

        if multiple:
            str_list.append(out_str)
            for st in str_list:
                await ctx.send(st)
        else:
            await ctx.send(out_str)

    @power.group(invoke_without_command=True)
    async def guild(self, ctx):
        """Sends graph of of guild gp"""
        #Should add text somewhere saying how long we are graphing. Also, what is that weird
        #text in the top left of the graph?
        file_name = 'data/' + str(ctx.message.guild.id) + 'guild_data.json'
        date_list = []
        gp_list = []
        with open(file_name, 'r') as guild_file:
            guild_data = json.loads(guild_file.read())
        for day in guild_data:
            date = datetime.datetime.fromisoformat(day['date'])
            gp = day['profile']['guildGalacticPower']
            date_list.append(date)
            gp_list.append(gp)


        growth_list = helper.get_growth_list(gp_list)

        fig, ax = plt.subplots()
        new_date_list = []
        for d in date_list:
            new_date_list.append(np.datetime64(d))
        display_date = mpl.dates.DateFormatter('%m-%d')
        ax.plot(new_date_list, gp_list)
        ax.xaxis.set_major_formatter(display_date)
        fig.savefig("graph.png")
        with open('graph.png', 'rb') as image:
            f=discord.File(image, filename="image.png")
        await ctx.send(file=f)
        out_str = ''
        for day in growth_list:
            out_str += "{}\n".format(day)
        #await ctx.send(out_str)


    @guild.command()
    async def growth(self, ctx, *args):
        """Graph all guild users growth for given number of days or weeks.
        Add the week argument to show growth by week instead of day. Defaults to 7 days or 2 weeks"""
        file_name = 'data/' + str(ctx.message.guild.id) + 'guild_data.json'
        date_list = []
        gp_list = []
        export_file_name = 'growth_graph.png'
        name_list = []
        #should be name: growth list
        user_dict = {}
        days = None
        member_list = []
        if "week" in args or 'weekly' in args or 'weeks' in args:
            graph_by_week = True
            week = 7
        else:
            graph_by_week = False
            week = 1
        for arg in args:
            try:
                days = int(arg)
                if not graph_by_week:
                    days +=1
            except ValueError:
                pass
        if not days:
            if graph_by_week:
                days = 2
            else:
                days = 8

        print ("days from args {}".format(days))
        with open(file_name, 'r') as guild_file:
            guild_data = json.loads(guild_file.read())
        length = len(guild_data) -1
        if length + 1 < days*week:
            days = int(length/week)
            if not graph_by_week:
                days +=1
            print ("changng days to {}.".format(days))

        #using length doesn't seem rigth
        for member in guild_data[length]['memberList']:
            member_list.append(helper.Member(member))
        #member_list = guild_data[length]['memberList']

        #for member in member_list:
        #    name_list.append(member['playerName'])

        for member in member_list:
            if graph_by_week:
                #This adds one more day for the initial growth to start from
                member.create_gp_lists(guild_data, (days*week)+1)
            else:
                member.create_gp_lists(guild_data, days)
            if graph_by_week:
                member.change_to_weekly(week)
        if graph_by_week:
            await ctx.send("Graphing gp growth for the last {} weeks.".format(days))
        else:
            await ctx.send("Graphing gp growth for the last {} days.".format(days -1))
        print ("We have {} days.".format(len(member_list[0].date_list)))

        def sort_func(k):
            return  sum(k.growth_list)

        member_list.sort(key=sort_func)
        member_list.reverse()
        # I think this is only for ticks. I don't like this 
        name_list = []
        for member in member_list:
            name_list.append(member.name)



        color_list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:brown', 'tab:olive', 'tab:red', 'tab:cyan', 'tab:gray', 'brown', 'yellow', 'olivedrab']
        fig = plt.figure(figsize=(20,5))
        ax = fig.add_axes([.1,.25,.9,.7])
        y_max = 0
        for user in member_list:
            user_max = 0
            last_day = 0
            ite = 0
            for day in user.growth_list:
                if day + last_day > user_max:
                    user_max = day + last_day
                ax.bar(member_list.index(user), day, bottom = last_day, color=color_list[ite])
                if ite < len(color_list) -1:
                    ite +=1
                else:
                    ite = 0
                #bar = ax.bar(user, day, bottom = last_day, label = user)
                #ax.bar_label(bar, label_type = 'center')
                last_day += day
            #y = sum(user_dict[user]) + sum(user_dict[user])/100
            #y = sum(user.growth_list) + 300
            y = user_max + 300
            plt.text(member_list.index(user) -.45, y, self.total_format(sum(user.growth_list)))
            if sum(user.growth_list) > y_max:
                y_max = sum(user.growth_list)
        #ax.set_xticks(range(len(user_dict)), name_list )
        plt.xticks(ticks = range(len(member_list)), labels =name_list, rotation =90)
        legend_list = []
        index_changer = 0
        date_list = member_list[0].date_list[::week]
        for date in date_list:
            c_index = date_list.index(date)
            #print (c_index, '> ', len(color_list))
            if c_index - index_changer >= len(color_list):
                index_changer += len(color_list)

            #print ("index: ", str(c_index - index_changer))
            if graph_by_week:
                label = f"week of {date.month}-{date.day}"
            else:
                label = date.date()
            l = mpatches.Patch(color=color_list[c_index - index_changer], label=label)
            legend_list.append(l)
            
        plt.legend(handles=legend_list, loc='upper right')
        plt.title("GP Growth per user by day")
        plt.ylim(0, y_max*1.1)

        #plt.xlabel('Members')
                #ax.bar(range(len(user_dict[user])), user_dict[user])
        #plt.tight_layout()
        print ('saving file')
        fig.savefig(export_file_name)


        with open(export_file_name, 'rb') as image:
            f=discord.File(image, filename=export_file_name)
        await ctx.send(file=f)
        #print (user_dict)


    @power.group(invoke_without_command=True)
    async def user(self, ctx, *args):
        """Gives the growth for the specified user"""
        file_name = 'data/' + str(ctx.message.guild.id) + 'guild_data.json'
        out_str = ''
        command_list = []
        members = []
        name_list = []
        name_dict = {}
 
        days = None
        for arg in args:
            try:
                days = int(arg)
            except ValueError:
                command_list.append(arg)
        if not days:
            days = 7
        # This is to add one more day for growth
        days += 1
        user_name = ' '.join(command_list)
         
        with open(file_name, 'r') as guild_file:
            guild_data = json.loads(guild_file.read())



        member_list = guild_data[-1]['memberList']
        for member in member_list:
            members.append(helper.Member(member))
            name_list.append(member['playerName'])
        for member in members:
            name_dict[member.id] = [member.name, member.tickets]

        #user_id, name = self.get_proper_name(user_name, name_dict)
        l = self.get_proper_name(user_name, name_dict)
        try:
            user_id = l[0]
            name = l[1]
        except TypeError:
            user_id = None
            name = None
        user_list = []
        for member in members:
            if member.name == name:
                user_list.append(member)

        if not user_id:
            out_str = "Could not find a member with that name. Here is a list of possible names:\n"
            for name in name_list:
                if name[0].casefold() == user_name[0].casefold():
                    out_str += name + '\n'
            await ctx.send(out_str)
            return


        if len(guild_data) < days:
            days = len(guild_data)

        def make_list(user_id):
            date_list = []
            gp_list = []
            out_str = ''
            for day in guild_data[-days:]:
                date = datetime.datetime.fromisoformat(day['date'])
                members = day['memberList']
                for member in members:
                    if member['playerId'] == user_id:
                        gp_list.append(member['galacticPower'])
                        gp = format(member['galacticPower'], ',d')
                        #out_str += "{}: {}\n".format(date.date(), gp)
                        date_list.append(date)

            growth_list = helper.get_growth_list(gp_list)
            date_list.pop(0)
            gp_list.pop(0)


            out_str += "History for {} for the last {} days.\n".format(name, len(growth_list))
            for ite in range(len(gp_list)):
                out_str += "{}-{}: {}. Growth: {}\n".format(date_list[ite].month, date_list[ite].day, format(gp_list[ite], ',d'), format(growth_list[ite], ',d'))

            out_str += "Total growth over the last {} days: {}.".format(len(growth_list), format(sum(growth_list), ',d'))

            return out_str
        

        for user  in user_list:
            out = make_list(user.id)
            await ctx.send(out)




    #@user.command()
    async def graph(self, ctx, *args):
        print (args)


