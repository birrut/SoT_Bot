import json
import requests
import mods
import sys
import os
import discord
from discord.ext import commands
import config
import helper

color_dict = {1:'Grey', 2:'Green', 3:'Blue', 4:'Purple', 5:'Gold'}

class Mod():
    def __init__(self, mod_json, character_list):
        self.characters = character_list

        shape_dic = {
                '1': "Square",
                '2': "Arrow",
                '3': "Diamond",
                '4': "Triangle",
                '5': "Circle",
                '6': "Cross"}

        set_dic = {
                '1': "Health",
                '2': "Offense",
                '3': "Defense",
                '4': "Speed",
                '5': "Crit Chance",
                '6': "Crit Damage",
                '7': "Potency",
                '8': "Tenacity"

                }
        self.primary_stat_id = mod_json['primary_stat']['stat_id']
        self.primary_value = mod_json['primary_stat']['display_value']
        self.primary_stat = mod_json['primary_stat']['name']
        self.slot_id = mod_json['slot']
        self.shape = shape_dic[str(self.slot_id)]
        # self.dot = str(self.def_id)[1]
        self.tier = mod_json['tier']
        self.rarity = mod_json['rarity']
        self.level = mod_json['level']
        self.set_id = mod_json['set']
        self.character = mod_json['character']
        self.total_number_of_rolls = 12
        try:
            self.set = set_dic[str(self.set_id)]
        except KeyError:
            print ("This is in set except")
            print (self.def_id)
            print (self.shape)

        # self.primary_value = mod_json['primaryStat']['stat']['statValueDecimal']
        self.level = mod_json['level']
        self.tier = mod_json['tier']
        self.secondary = mod_json['secondary_stats']
        self.secondary_list = []
        for stat in self.secondary:
            new_stat = self.add_percent(stat)
            self.secondary_list.append(new_stat)


        self.get_display_name()
        self.update_total_percent()
        self.get_chance()

    def __repr__(self):
        """Returns string of mod"""
        # out = self.character_display_name
        out = ''
        out += f"\nLevel: {self.level} Color: {color_dict[self.tier]} {'•'*self.rarity}, Set: {self.set}, {self.shape} Percent of max roll: {self.total_percent}%\n"
        if self.possible:
            out += f"Remaining rolls: {self.remaining_rolls}. Chance to hit 5 speed rolls={self.chance_for_five}\n"
        try:
            #out += f"{self.stat_dic[self.primary_stat_id][0]}: {str(self.display_value)}{self.suffix}"
            out += f"Primary: {self.primary_stat}: {str(self.primary_value)}"
        except KeyError:
            out += f"{self.primary_stat_id}: {str(self.primary_value)} \n"
        for second in self.secondary_list:
            try:
                # out += f"\n{second['display_value']}{second['suffix']} {second['stat']} Rolls: {second['rolls']}"
                out += f"\n{second['name']}: {second['display_value']} Rolls: {second['roll']}, Avg: {second['avg_roll']}, Max: {second['max']} Min: {second['min']} Percent of max: {second['percent_of_max']}%"

                #out += str(second['value']) + '\n'
            except Exception as e:
                print ('error', second)
                raise e
                #print (f"Don't know this id: {second['id']}")

            #out += f" Min roll: {second['min_roll']} Avg roll: {second['avg_roll']} Max roll: {second['max_roll']}"
            #out += f"\nPercent of max: {second['percent_of_max']}"
        out +='\n'

        return out

    def get_chance(self):
        """this returns the chance of hitting 5 speed rolls."""
        num_of_rolls = 0
        num_speed_rolls = 0
        for stat in self.secondary_list:
            num_of_rolls += stat['roll']
            if stat['stat_id'] == 5:
                num_speed_rolls = stat['roll']
        self.possible = False
        if num_speed_rolls > 0:
            self.possible = True
        else:
            self.chance_for_five = 0
            return
        speed_rolls_remaining = int(5 - num_speed_rolls)
        self.remaining_rolls = int(self.total_number_of_rolls - num_of_rolls)
        try:
            self.chance_for_five = helper.cumulative(self.remaining_rolls, speed_rolls_remaining)
            #print(self.chance_for_five)

        except (ZeroDivisionError, TypeError) as e:
            # This is for mods that have no remaining rolls left
            self.chance_for_five = 0
    
    def get_display_name(self):
        for character in self.characters:
            if character['base_id'] == self.character:
                self.character_display_name = character['name']

    def update_total_percent(self):
        """This cannot be called before update_secondary_list"""
        total_percent = 0
        for stat in self.secondary_list:
            total_percent += float(stat['percent_of_max'])
        try:
            self.total_percent = round(total_percent/len(self.secondary_list),2)
        except ZeroDivisionError:
            self.total_percent = 0


    def add_percent(self, secondary_dictionary):
        # this should be called once for each stat
        m_stats = mods.modStats()
        stats = m_stats.get_stat_details(secondary_dictionary['stat_id'], self.rarity)
        if '%' in secondary_dictionary['display_value']:
            value = secondary_dictionary['display_value'].replace('%', '')
        else:
            value = secondary_dictionary['display_value']
        avg = round(float(value)/int(secondary_dictionary['roll']),2)
        secondary_dictionary['avg_roll'] = avg
        percent = round(avg/stats['max'],2)
        if type(stats) is dict:
            secondary_dictionary.update(stats)

        secondary_dictionary['percent_of_max'] = percent
        return secondary_dictionary



    def create_stat_dic(self):
        self.stat_dic[1] = ["Health", '', 'health']
        self.stat_dic[5] = ["Speed", '', 'speed']
        self.stat_dic[16] = ["Crit Damage", '%', None]
        self.stat_dic[17] = ["Potency", '%', 'potency']
        self.stat_dic[18] = ["Tenacity", '%', 'tenacity']
        self.stat_dic[28] = ["Protection", '', 'protection']
        self.stat_dic[41] = ["Offense", '', 'offense']
        self.stat_dic[42] = ["Defense", '', 'defense']
        self.stat_dic[48] = ["Offense", '%', 'offenseP']
        self.stat_dic[49] = ["Defense", '%', 'defenseP']
        self.stat_dic[52] = ["Accuracy", '%', None]
        self.stat_dic[53] = ["Crit Chance", '%', 'cc']
        self.stat_dic[54] = ["Crit Avoidance", '%', None]
        self.stat_dic[55] = ["Health", '%', 'healthP']
        self.stat_dic[56] = ["Protection", '%', 'protectionP']



def make_call(player_id):
    url = f'https://swgoh.gg/api/player/{str(player_id)}/mods'
    payload = {}
    headers = {"User-Agent": 'PostmanRuntime/7.29.0', "Accept": '*/*'}
    print (url)
    try:
        #response = requests.request(url, timeout=15)
        response = requests.request("GET", url, headers=headers, data=payload)
    except Timeout:
        return
    print(response.status_code)

    if response.status_code == 200:
        return response.json()

def order_mods(mod):

    if mod.chance_for_five == 1:
        return 0
    else:
        score = (mod.chance_for_five + mod.total_percent)/2
    return score
    # return mod.total_percent + mod.chance_for_five
    # return mod.total_percent



class ModPrinter(commands.Cog):
    """This is in beta. This helps with mods"""
    def __init__(self, bot):
        with open('data/characters.json', 'r') as data_file:
            self.characters = json.loads(data_file.read())
        self.bot = bot
        print('Mod cog initialized')

    @commands.command(name="register")
    async def register(self, ctx, *args):
        """Use this to register you allycode to your discord user name"""
        # This shouldn't be in this cog
        if len(args) > 1:
            await ctx.send("Input is too long")
            return
        ally_code = args[0]
        if len(ally_code) == 9:
            try:
                int(ally_code)
            except ValueError:
                await ctx.send("Please specify your 9 digit allycode with no hyphens")
                return
        else:
            await ctx.send("Please specify your 9 digit allycode with no hyphens")
            return
        discord_id = ctx.author.id
        with open('data/users.json', 'r') as user_file:
            user_list = json.loads(user_file.read())

        if discord_id not in user_list:
            new_user = {discord_id: ally_code}
            user_list.append(new_user)

        with open('data/users.json', 'w') as user_file:
            user_file.write(json.dumps(user_list))

        await ctx.send("You are now registered!")

    # @commands.command(name="unregister")
    async def unregister(self, ctx):
        """Use this to unregister"""
        with open('data/users.json', 'r') as user_file:
            user_list = json.loads(user_file.read())

        out_list = []
        for user in user_list:
            #if user 
            new_user = {discord_id: ally_code}
            user_list.append(new_user)



    @commands.command(name="highest_mods")
    async def highest_mods(self, ctx, *args):
        """This returns your mods with the highest percent rolls and the highest chance of getting 5 speed hits.
        You can pass a number of mods you would like, or it will default to 5.
        You can also use the require key word to specify that the mods returned have a specific secondary stat.
        e.g.: $highest_mods 15 require speed"""
        number_of_mods = 5
        Filter = False
        attr_list = ['Speed', 'Defense', 'Offense', 'Potency', 'Tenacity', 'Protection', 'Cc']
        args = list(args)
        try:
            number_of_mods = int(args[0])
            args.pop(0)
        except (ValueError, IndexError) as e:
            print(e)

        if len(args) > 1:
            if args[0].casefold() == "Require".casefold():
                Filter = True
                filter_attr = None
                for attr in attr_list:
                    if args[1].casefold() == attr.casefold():
                        filter_attr = attr
                        if attr == 'Cc':
                            filter_attr = 'Critical Chance'
                if filter_attr == None:
                    await ctx.send(f"I don't recognize that attribute. Here are your choices: {' '.join(attr_list)}")

                    return

        with open('data/users.json', 'r') as user_file:
            user_list = json.loads(user_file.read())

        ally_code = None 
        for user in user_list:
            print(user)
            if str(ctx.author.id) in user:
                ally_code = user[str(ctx.author.id)]
        if ally_code == None:
            await ctx.send("You are not registered. Please run $register 123123123")
        
        m_json = make_call(ally_code)
        # Handle wrong ally code (no response) here

        mod_list = []
        for mod in m_json['mods']:
            m = Mod(mod, self.characters)
            mod_list.append(m)
        filter_mod_list = []
        if Filter:
            for mod in mod_list:
                for stat in mod.secondary_list:
                    if stat['name'] == filter_attr:
                        if mod.remaining_rolls != 0.0:
                            filter_mod_list.append(mod)

            sorted_list = sorted(filter_mod_list, key=order_mods)
        else:
            sorted_list = sorted(mod_list, key=order_mods)
        sorted_list.reverse()
        if Filter:
            emb = discord.Embed(title=f'Highest Percent Mods with {filter_attr}', color=discord.Color.blue())
        else:
            emb = discord.Embed(title='Highest Percent Mods', color=discord.Color.blue())
        emb_list = []
        out_str = ''
        for mod in sorted_list[:number_of_mods]:
            out_str += str(mod)
            emb.add_field(name=mod.character_display_name, value=str(mod), inline=False)
            if len(out_str) > 5000:
                out_str = ''
                emb_list.append(emb)
                if Filter:
                    emb = discord.Embed(title=f'Highest Percent Mods with {filter_attr}', color=discord.Color.blue())
                else:
                    emb = discord.Embed(title='Highest Percent Mods', color=discord.Color.blue())

        if len(emb_list) == 0:
            emb_list.append(emb)

        for emb in emb_list:
            #print(emb.field)
            emb.set_thumbnail(url='attachment://bot.png')
            image = discord.File('bot.png', filename='bot.png')
            await ctx.send(file=image, embed=emb)
        # await ctx.send(out_str)



if __name__ == "__main__":
    m_json = make_call(482764294)
    mod_list = []
    for mod in m_json['mods']:
        m = Mod(mod)
        mod_list.append(m)
        if m.character == "POGGLETHELESSER":
            pass
             #print(m)
    sorted_list = sorted(mod_list, key=order_mods)
    sorted_list.reverse()
    for mod in sorted_list[:10]:
        print(mod)

