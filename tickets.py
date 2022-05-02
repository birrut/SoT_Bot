import json
import requests
from requests.exceptions import Timeout
import datetime
import calendar
import asyncio
import discord
from discord.ext import commands, tasks
from asyncio import exceptions
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import helper
import config


class Tickets(commands.Cog):
    """Handles all the commands for managing daily tickets"""
    def __init__(self, bot):
        self.bot = bot
        self.schedule_ticket_call.start()
        # At some point, this should be in a config file
        self.server_list = ['884464695476625428', '888611226593136690']
        self.server_data_list = []
        for server in self.server_list:
            self.server_data = {}
            self.server_data['server'] = server
            if server == '888611226593136690':
                self.server_data['channel'] = '888611287112749106'
            elif server == '884464695476625428':
                self.server_data['channel'] = '888234595269619772'

            self.server_data_list.append(self.server_data)

        print('Tickets cog initialized')

    def get_proper_name(self, name, dic_list):
        """Gets proper name from command
        takes a name from command and a one days list of dictionaries of form
        {id:[name, tickets]} and returns id."""

        out_list = []
        # This checks for an exact (minus case) match
        for key in dic_list:
            # print(dic_list[key])
            try:
                if dic_list[key][0].casefold() == name.casefold():
                    out_list.append((key, dic_list[key][0]))
                    return [key, dic_list[key][0]]
            except TypeError:
                pass
                # print("Do we ever get here?")
        # this checks for a partial match
        if not out_list:
            for key in dic_list:
                try:
                    if name.casefold() in dic_list[key][0].casefold():
                        # print(key, dic_list[key])
                        # print(dic_list[key][1])
                        out_list.append((key, dic_list[key][0]))
                except TypeError:
                    pass

        if len(out_list) == 1:
            return out_list[0]

    def total_format(self, number):
        """Takes an int and returns a decimal string with letter to simulate exponents"""
        f_list = ['', 'k', 'm']
        mag = 0
        while number > 1000:
            mag += 1
            number = number / 1000
        return "{}{}".format(round(number), f_list[mag])

    def save_gp_info(self, guild_json, file_name):
        """this is called automatically and saves the guild gp data."""
        write_list = []
        print('this is how long the input was.')
        print(len(guild_json))
        print(file_name)

        now = datetime.datetime.utcnow()
        guild_json = guild_json['guild']
        guild_json['utc time'] = str(now)
        guild_json['date'] = str(datetime.datetime.now())
        this_update_time = now

        try:
            with open(file_name, 'r') as read_file:
                old_data = json.loads(read_file.read())
        except FileNotFoundError:
            old_data = [guild_json]

        for day in old_data:
            last_update = datetime.datetime.fromisoformat(day['date'])
            # Should check guild update time here
            if last_update.date() == this_update_time.date():
                index = old_data.index(day)
                old_data.pop(index)
                print("Remvoing ", str(last_update.date()))
        if len(old_data):
            write_list = old_data
        write_list.append(guild_json)

        with open(file_name, 'w') as write_file:
            write_file.write(json.dumps(write_list))

    def delete_day(self, f, date):
        """Function that actually deletes the day from the json file."""
        print('we are thinking about deleting a day')
        out_dictionary_list = []
        out_str = ''
        # print(date)
        with open(f, 'r') as input_file:
            d_list = json.loads(input_file.read())
            print("Original Length: ", len(d_list))
            orig_len = len(d_list)
            for d in d_list:
                if date == datetime.datetime.fromisoformat(d['date']).date():
                    print("Removing: ", datetime.datetime.fromisoformat(d['date']).date())
                else:
                    out_dictionary_list.append(d)
        end_len = len(out_dictionary_list)
        with open(f, 'w') as out_file:
            # print(out_dictionary_list)
            print(len(out_dictionary_list))
            out_file.write(json.dumps(out_dictionary_list))
        if end_len < orig_len:
            out_str = "Number of days stored changed from {} to {}.".format(orig_len, end_len)
        else:
            out_str = "No days to remove"
        return out_str

    def day_exists(self, f, date):
        with open(f, 'r') as in_file:
            day_list = json.loads(in_file.read())

        for day in day_list:

            if datetime.datetime.fromisoformat(day['date']).date() == date:
                return True
        return False

    def check(self, reaction, user):
        """helper function for checking for reaction"""
        print("We don't use this, right?")
        if user != self.bot.user:
            return True

    # Need to make this command work on guild_json as well as json
    # @commands.has_role("Officer")
    # @commands.command("remove_day")
    async def remove_day(self, ctx):
        """Removes Specified day from ticket list.
        This can only be called by an officer. Supply date of day you want removed in the format YYYY-MM-DD"""
        file_name = 'data/' + str(ctx.message.guild.id) + ".json"
        message_word_list = ctx.message.content.split()
        input_date = message_word_list[1:]
        # get input date
        date = datetime.datetime.fromisoformat(input_date[0]).date()
        if self.day_exists(file_name, date):
            mess = await ctx.send("Would you like to remove this day? Please respond!")
            await mess.add_reaction('✅')
            await mess.add_reaction('❌')
        else:
            await ctx.send("There is no day stored that matches that date. Please provide date in the format YYY-MM-DD")
            return

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=10, check=self.check)
        except exceptions.TimeoutError:
            out_str = "No Day Removed"
            await ctx.send(out_str)
            return
            print("They didn't say anything")
        print('do we ever get here?')
        # print(command)
        if reaction.emoji == '✅':
            out_str = self.delete_day(file_name, date)
        else:
            out_str = "No Day Removed"
        await ctx.send(out_str)

    @commands.command("rerun")
    async def rerun(self, ctx, message_id):
        """This is for if the daily ticket call didn't work, but Bobba's bot got called.
        Pass id of Bobba's message. This might not work if there is a new person since last ticket check"""
        new_dic = {}

        # get message
        old_message = await ctx.fetch_message(message_id)
        time = old_message.created_at - datetime.timedelta(hours=8)

        # read from guild_data
        # in_file = 'data/' +  str(ctx.message.guild.id) + "guild_data.json"
        write_file = 'data/' + str(ctx.message.guild.id) + ".json"
        with open(write_file, 'r') as guild_data:
            guild_info = json.loads(guild_data.read())
        guild_list = guild_info[-1]
        print(guild_list)
        new_dic['date'] = str(time)
        new_dic['guild name'] = guild_list['guild name']

        for x in old_message.embeds:
            ticket_string = x.description

        ticket_list = ticket_string.split(':')
        out_list = []
        for x in ticket_list:
            try:
                item_list = x.split("`")
                for item in item_list:
                    if item != "":
                        out_list.append(item.strip())
            except AttributeError:
                out_list.append(x.strip())
        ticket_list = list(reversed(out_list))
        number_list = [int(x) for x in ticket_list[1::2]]
        print(number_list)

        for name in ticket_list[::2]:
            for member in guild_list:
                try:
                    if name in guild_list[member]:
                        new_dic[member] = [name, int(ticket_list[ticket_list.index(name)+1])]
                except TypeError:
                    pass
        new_dic['total'] = sum(number_list)
        new_dic['average'] = round(sum(number_list)/len(number_list))
        print(new_dic)

        # create message
        await ctx.send(f"Total tickets was {new_dic['total']} and the average was {new_dic['average']}")

        # write data
        print(len(guild_info))
        guild_info.append(new_dic)
        print(len(guild_info))
        with open(write_file, 'w') as out_file:
            out_file.write(json.dumps(guild_info))

    # This doesn't have gp, and we would need to get ID's from json and match with names from Bobba's Bot
    # @bot.listen('on_message')
    # @commands.Cog.listener("on_message")
    async def on_message(self, message):
        """Currently on using this to respond to the message from Bobba's bot, is there a better way to do this?"""
        if message.author == self.bot.user:
            return

        if message.author.id == 718470614926491729:
            # guild_id =  message.guild.id
            # for x in message.embeds:
            #    average_daily = get_daily_average(x.description, guild_id)
            for x in message.embeds:
                guild_name_tuple = x.title.partition('for ')[-1:]
                for name in guild_name_tuple:
                    guild_name = name
                ticket_string = x.description
            # out_file = str(message.guild.id) +  ".json"
            ticket_list = ticket_string.split(':')
            message_dict = {}
            message_dict['guild_name'] = guild_name
            message_dict['guild_id'] = message.guild.id
            message_dict['ticket_list'] = ticket_list
            # print(ticket_list)
            daily_list = self.get_daily_average(message_dict)
            print(daily_list)
            average_daily = daily_list[0]
            daily_total = daily_list[1]
            record_average = daily_list[2]
            record_total = daily_list[3]
            max_average = daily_list[4]
            max_total = daily_list[5]

            out_str = f"The average daily tickets for today was {average_daily}, and the total was {daily_total}. The record average is {max_average} and the record total is {max_total}"
            await message.channel.send(out_str)

            if record_average:
                await message.channel.send("New record average!!!!")
            if record_total:
                await message.channel.send("New record total!!!")

            return

    async def get_daily_average(self, channel, date):
        """Gets the daily average."""

        # This is UTC time
        guild_reset_time = datetime.time(hour=1, minute=30)
        # reset_time = datetime.datetime.combine(datetime.date.today(), guild_reset_time)
        reset_time = datetime.datetime.combine(datetime.datetime.utcnow(), guild_reset_time)

        read_file = 'data/' + str(channel.guild.id) + "guild_data.json"
        write_file = 'data/' + str(channel.guild.id) + ".json"

        member_list = []
        out_dict = {}
        out_str = ''
        out_dict['utc time'] = str(date)
        out_dict['date'] = str(date - datetime.timedelta(hours=7))
        with open(read_file, 'r') as data:
            day_list = json.loads(data.read())
        for day in day_list:
            file_date = datetime.datetime.fromisoformat(day['utc time'])
            # print('here', file_date.date(), date.date())
            if file_date.date() == date.date():
                guild_name = day['profile']['name']
                members = day['memberList']
        try:
            out_dict['guild name'] = guild_name
        except UnboundLocalError:
            print("no day matching today")
        for member in members:
            member_list.append(helper.Member(member))

        def sort_func(user):
            return user.tickets
        member_list.sort(key=sort_func)
        for member in member_list:
            out_str += f"`{member.tickets}`: {member.name}\n"
            out_dict[member.id] = [member.name, member.tickets]
            # out_dict[member.name] = member.tickets

        total = sum(member.tickets for member in member_list)
        avg = round(total/len(member_list))
        out_dict['total'] = total
        out_dict['average'] = avg
        with open(write_file, 'r') as inp:
            old_data = json.loads(inp.read())
        print(len(old_data))
        max_tickets = 0
        avg_tickets = 0

        for day in old_data:
            last_update = datetime.datetime.fromisoformat(day['date'])
            # Need to check guild reset time as well
            # print(f"{date} - {self.reset_time}")
            if last_update.date() == date.date() and date < reset_time:
                print("removing older data: ", date.date())
                index = old_data.index(day)
                old_data.pop(index)
            if day['total'] > max_tickets:
                max_tickets = day['total']
            if day['average'] > avg_tickets:
                avg_tickets = day['average']

        writing = False
        old_data.append(out_dict)
        print(len(old_data))
        print(date)
        print(reset_time)
        if date < reset_time:
            writing = True
            with open(write_file, 'w') as out:
                out.write(json.dumps(old_data))

        out_str += f"The average for today was: {avg}, the max average is {avg_tickets}\n"
        out_str += f"The total for today was: {total}, and the max total is {max_tickets}\n"

        emb = discord.Embed(title=f'Daily Tickets for {guild_name}', description=out_str, color=discord.Color.blue())
        emb.set_thumbnail(url='attachment://bot.png')
        image = discord.File('bot.png', filename='bot.png')
        await channel.send(file=image, embed=emb)
        if not writing:
            await channel.send("Not writing because call was after reset")
        if total > max_tickets:
            await channel.send("New record total!")

        if avg > avg_tickets:
            await channel.send("New average record!")
        # await channel.send(out_str)

    @commands.command(name="history")
    async def history(self, ctx, *args):
        """History for the specified user. Can take any days or gives 7 by default"""
        in_file = 'data/' + str(ctx.message.guild.id) + ".json"
        not_name_list = ['utc time', 'date', 'guild name', 'average', 'total']
        command_list = []
        days = None
        out_str = ''
        for arg in args:
            try:
                days = int(arg)
            except ValueError:
                command_list.append(arg)

        if not days:
            days = 7

        if len(args) == 0:
            await ctx.send("Please specify a user")
            return

        with open(in_file, 'r') as in_data:
            json_list = json.loads(in_data.read())
        test_members = json_list[-1]

        in_str = ' '.join(command_list)
        try:
            player_id, name = self.get_proper_name(in_str, test_members)
        except TypeError:
            player_id = None

        if not player_id:
            out_str += f"No member named {in_str}. Try one of these:\n"
            for member in test_members:
                if member not in not_name_list:
                    name = test_members[member][0].casefold()[0]

                    if name == in_str.casefold()[0]:
                        out_str += test_members[member][0] + '\n'
            await ctx.send(out_str)
            return
        user_list = []
        for member in test_members:
            if member not in not_name_list:
                if test_members[member][0] == name:
                    user_list.append([member, test_members[member][0]])

        if len(json_list) < days:
            days = len(json_list)

        def build_str(user_list):
            user_days = days
            history_list = []
            date_list = []
            for day in json_list[-user_days:]:
                date = datetime.datetime.fromisoformat(day['date'])
                for member in day:
                    # member = Member(pot_member)
                    if member == user_list[0]:
                        history_list.append(day[member][1])
                        date_list.append(date)
            out_str = f"Ticket history for {user[1]} for the last {user_days} days.\n"
            if len(history_list) < user_days:
                user_days = len(history_list)
                out_str = f"I only have {user_days} days of data for {name}.\n"
            for day in date_list:
                num = history_list[date_list.index(day)]
                avg = format(int(sum(history_list)/len(history_list)), ',d')
                out_str += f"{day.month}-{day.day}: {num}\n"
            out_str += f"The average tickets for {name} over the last {user_days} days is: {avg}"
            return out_str

        for user in user_list:
            out = build_str(user)
            await ctx.send(out)

    @commands.command(name="average")
    # @commands.hybrid_command()
    async def average(self, ctx):
        """Sorts members by tickets averaged over the given number of days.
        Defaults to 7"""
        in_file = 'data/' + str(ctx.message.guild.id) + ".json"
        out_str = ''
        message_word_list = ctx.message.content.split()
        not_name_list = ['utc time', 'date', 'guild name', 'average', 'total']
        if len(message_word_list) == 2:
            try:
                days_to_process = int(message_word_list[1])
            except ValueError:
                out_str = "Sorry, that isn't a number, defaulting to 7\n"
                days_to_process = 7
        else:
            days_to_process = 7
        id_list = []
        avg_dict = {}
        name_dict = {}
        dict0 = {}
        dictsub300 = {}
        dictsub600 = {}
        dict600 = {}
        day_number = 0

        with open(in_file, 'r') as in_data:
            dictionary_list = json.loads(in_data.read())
        day_number = len(dictionary_list)
        for day in dictionary_list[-1:]:
            for key in day:
                try:
                    if key not in not_name_list:
                        id_list.append(key)
                        name_dict[key] = day[key][0]
                except TypeError:
                    pass

        for player_id in id_list:
            number_list = []
            for day in dictionary_list[-days_to_process:]:
                try:
                    # print(day[player_id])
                    number_list.append(day[player_id][1])
                except KeyError:
                    pass
            avg_dict[player_id] = (round(sum(number_list)/len(number_list)), len(number_list))
        for player_id in avg_dict:
            if avg_dict[player_id][0] == 0:
                dict0[player_id] = avg_dict[player_id]
            elif avg_dict[player_id][0] < 300:
                dictsub300[player_id] = avg_dict[player_id]
            elif avg_dict[player_id][0] < 600:
                dictsub600[player_id] = avg_dict[player_id]
            else:
                dict600[player_id] = avg_dict[player_id]
        if day_number < days_to_process:
            # out_str += "I don't have data for {} days, I only have {} days. \n".format(days_to_process, day_number)
            days_to_process = day_number

        dict_list = [dict0, dictsub300, dictsub600, dict600]
        str_list = ['0', 'between 0-299', 'between 300-599', '600']
        str_dict = {
                '0': "0",
                'sub300': 'between 0-299',
                'sub600': 'between 300-599',
                '600': '600'}
        ite = 0
        emb = discord.Embed(title=f"Ticket History for the last {days_to_process} days", color=discord.Color.green())

        for dic in dict_list:
            # dic.sort(dic.items(), key=lambda item:item[1])
            dic = dict(sorted(dic.items(), key=lambda item:item[1]))
            # out_str += f"\n**Members who averaged {str_list[ite]}:**\n"
            for player_id in dic:
                out_str += f"{name_dict[player_id]}: {str(dic[player_id][0])}\n"
                if dic[player_id][1] < days_to_process:
                    # This removes the new line character
                    # print(out_str[-2:])
                    out_str = out_str[:-1]
                    out_str += f" (I only have {dic[player_id][1]} days) \n"
                # else:
                #    out_str +='\n'
            if out_str == '':
                out_str = "Nobody averaged {}".format(str_list[ite])
            emb.add_field(name =f"\n**Members who averaged {str_list[ite]}:**\n", value=out_str, inline=False)
            out_str = ''
            ite +=1



        # return out_str
        # await ctx.send(out_str)
        emb.set_thumbnail(url='attachment://bot.png')
        image = discord.File('bot.png', filename='bot.png')
        await ctx.send(file=image, embed=emb)


    @commands.command(name="average_history")
    async def average_list(self, ctx):
        """returns the total average with a graph. 
        Defaults to 7, but can take any number of days"""
        message_word_list = ctx.message.content.split()
        out_number = 7
        str_list = []
        out_str = ''
        out_list = []
        date_list = []
        in_file = 'data/' +  str(ctx.message.guild.id) + ".json"

        with open (in_file, 'r') as in_data:
            data = json.loads(in_data.read())

        if len(message_word_list) > 1:
            try:
                out_number = int(message_word_list[1])
                if out_number > len(data):
                    out_number = len(data)
                # out_str = "Trying to get the average for the last {} days.\n".format(out_number)
            except ValueError:
                out_str = "Sorry, that isn't a number, defaulting to 7\n"
                out_number = 7

        with open (in_file, 'r') as in_data:
            data = json.loads(in_data.read())

        for day in data[-out_number:]:
            out_list.append(day['average'])

        old_month = datetime.datetime.fromisoformat(data[-out_number]['date']).month
        counter = 0
        maxavg = max(out_list)
        minavg = min(out_list)
        multiple = False
        end_of_month = False
        for day in data[-out_number:]:
            # out_list.append(day['average'])
            date_list.append(day['date'])
            date = datetime.datetime.fromisoformat(day['date'])
            # date_list.append(date)
            # date_list.append(int(date.day))
            month = date.month
            day_number = date.day
            if old_month != month:
                end_of_month = True
                old_month = month
                counter = 0

            if counter % 5 == 0:
                out_str +="\n"
            counter +=1
            if len(out_str) >= 1000 or end_of_month:
                multiple = True
                first_str = out_str
                out_str = ''
                str_list.append(first_str)

            if day['average'] == maxavg or day['average'] ==minavg :
                out_str += f"{month}-{day_number}: **{day['average']}** "
            else:
                out_str += f"{month}-{day_number}: {day['average']} "
            end_of_month = False
        total = round(sum(out_list)/len(out_list))
        out_str += ("\nThe average of the averages is {}.".format(total))
        fig, ax = plt.subplots()
        new_list = []
        for d in date_list:
            new_list.append(np.datetime64(d))
        # graph_dates = np.arange(new_list)
        f_date = mpl.dates.DateFormatter('%m-%d')
        ax.scatter(new_list, out_list)
        ax.xaxis.set_major_formatter(f_date)
        ax.set_ylim([200, 600])
        new_date_list = [x for x in range(len(new_list))]

        # x = np.array(new_date_list)
        # y = np.array(out_list)
        x = new_date_list
        y = out_list
        linear_model = np.polyfit(x,y,2)
        linear_model_fn = np.poly1d(linear_model)
        x_s = np.arange(0,out_number)
        plt.plot(new_list, linear_model_fn(x_s))
        
        fig.savefig('plot.png')
        with open('plot.png', 'rb') as image:
            f=discord.File(image, filename="graph.png")

        await ctx.send(file=f)
        
        emb = discord.Embed(title=f"Ticket History Average for {out_number} days", colo=discord.Color.green())
        if multiple:
            str_list.append(out_str)
            for out_str in str_list:
                month = calendar.month_name[int(out_str.split('-')[0])]
                emb.add_field(name=f"{month}:", value=out_str, inline=False)
            await ctx.send(embed=emb)
                # if out_str != str_list[-1]:
                #    print('here')
                #    emb = discord.Embed(title=f"Ticket History Average for {out_number} days Continued", colo=discord.Color.green())
            
        else:
            # month = calendar.month_name[int(out_str.split('-')[0])]
            emb.add_field(name=f"Daily Average:", value=out_str, inline=False)
            await ctx.send(embed=emb)


    @commands.has_role("Officer")
    @commands.command(name="check_tickets")
    async def check_tickets(self, ctx=None, channel=None):
        """This is called automatically. It gets the ticket data, saves it in two places, and prints. 
        This can also be called manually by an officer if there was an error."""

        print('Checking Tickets...')
        out_str = ''
        URL = 'https://swgoh.shittybots.me/api/guild/'
        headers = {'shittybot': config.S_AUTH}
        last_update = []
        try:
            channel = ctx.channel
        except AttributeError:
            channel = channel
        

        final_url = URL + config.ALLY_CODE
        try:
            response = requests.get(final_url, headers=headers, timeout=15)
        except Timeout:
            try:
                await channel.send("It seems like the api is having timeout issues, please try again later")
                print(response.status_code)
            except AttributeError:
                await channel.send("It seems like the api is having issues, please try again later")
                print(response.status_code)
            return
        print(response.status_code)
        
        if response.status_code == 429:
            await channel.send("Too many requests to API, please try again later")
            return
        elif response.status_code == 200:
            ticket_list = []
            r_json = response.json()
            guild_file_name = 'data/' + str(channel.guild.id) + 'guild_data.json'
            self.save_gp_info(r_json, guild_file_name)

        date = datetime.datetime.utcnow()
        await self.get_daily_average(channel, date)



    @tasks.loop(hours=24)
    async def schedule_ticket_call(self):
        print("Making ticket_call")
        print(datetime.datetime.now())

        for server in self.server_data_list:
            channel_number = int(server['channel'])
            channel = self.bot.get_channel(channel_number)
            self.channel = channel
            try:
                # await channel.send('we should run the check tickets command now!')
                await self.check_tickets(channel=channel)
            except AttributeError as e:
                print('maybe wrong guild? This is in the if statement')
                raise e

    @schedule_ticket_call.before_loop
    async def before_ticket_loop(self):
        print('waiting...')
        await self.bot.wait_until_ready()
        guild_reset_time = datetime.time(hour = 1, minute = 30)
        # guild_reset_time = datetime.time(hour = 22, minute = 31)
        reset_time = datetime.datetime.combine(datetime.datetime.utcnow(), guild_reset_time)
        # self.reset_time = reset_time
        run_time = reset_time - datetime.timedelta(seconds=30)
        now = datetime.datetime.utcnow()
        print(run_time)
        print(f"Waiting for {(run_time - now).seconds} seconds.")
        # print((reset_time-now).seconds)
        await asyncio.sleep((run_time - now).seconds)
       


