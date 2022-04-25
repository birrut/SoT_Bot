import json
import requests
from requests.exceptions import Timeout
import mods
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import config


class Unit():
    def __init__(self, unit_json):
        self.rarity = unit_json['currentRarity']
        self.level = unit_json['currentLevel']
        self.gear = unit_json['currentTier']
        self.unit_def = unit_json['definitionId']
        self.mod_list = []
        if len(unit_json['equippedStatModList']) > 0:
            self.create_mod_list(unit_json['equippedStatModList'])

    def __repr__(self):
        #out = str(self.rarity) + '\n'
        out = f"{self.unit_def} Stars: {'*'*self.rarity} Level: {self.level} Gear: {self.gear} \n"
        #out = "Stars: " + '*'*self.rarity + '\n'
        #out += "Level: " + str(self.level) + '\n'
        #out += "Gear: " + str(self.gear) + '\n'
        for mod in self.mod_list:
            out +="Mod: "
            out += str(mod) + '\n'
        return out

    def get_mod_by_shape(self, shape):
        """Takes a string representing a shape"""
        for mod in self.mod_list:
            if mod.shape == shape:
                #print (self.unit_def)
                return mod
        

    def create_mod_list(self, mod_list):
        #print (self.unit_def)
        for mod in mod_list:
            self.mod_list.append(Mod(mod, self.unit_def))
        

class Mod():
    def __init__(self, mod_json, character):
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
        self.character = character
        self.primary_stat_id = mod_json['primaryStat']['stat']['unitStatId']
        self.primary_value = mod_json['primaryStat']['stat']['statValueDecimal']
        self.def_id = mod_json['definitionId']
        self.shape = shape_dic[str(self.def_id)[2]]
        self.dot = str(self.def_id)[1]
        try:
            self.set = set_dic[str(self.def_id)[0]]
        except KeyError:
            print ("This is in set except")
            print (self.def_id)
            print (self.shape)

        #self.primary_value = mod_json['primaryStat']['stat']['statValueDecimal']
        self.level = mod_json['level']
        self.tier = mod_json['tier']
        self.secondary_list = []
        self.stat_dic = {}
        self.create_stat_dic()

        try:
            self.suffix = self.stat_dic[self.primary_stat_id][1]
        except KeyError:
            print ("are we here?")
            print (self.shape)
            print (self.primary_stat_id)
            print (self.primary_value)
            #print (
        if self.suffix == '%':
            self.display_value = self.primary_value/100
        else:
            self.display_value = round(self.primary_value/10000)


        for stat in mod_json['secondaryStatList']:
            self.update_secondary_list(stat)

        self.update_total_percent()

    def __repr__(self):
        out = self.character
        out += f'\nLevel: {self.level} Tier: {self.tier} Set: {self.set}, {self.shape}, {self.dot} t_p: {self.total_percent}\n'
        try:
            out += f"{self.stat_dic[self.primary_stat_id][0]}: {str(self.display_value)}{self.suffix}"
        except KeyError:
            out += f"{self.primary_stat_id}: {str(self.primary_value)} \n"
        for second in self.secondary_list:
            try:
                #out += f"\n{self.stat_dic[second['id']][0]} = {second['value']}{self.stat_dic[second['id']][1]}"
                out += f"\n{second['display_value']}{second['suffix']} {second['stat']} Rolls: {second['rolls']}"

                #out += str(second['value']) + '\n'
            except:
                print (f"Don't know this id: {second['id']}")
                out += f"\n{second['id']} = "
                out += str(second['value'])

            out += f" Min roll: {second['min_roll']} Avg roll: {second['avg_roll']} Max roll: {second['max_roll']}"
            out += f"\nPercent of max: {second['percent_of_max']}"
        out +='\n'

        return out


    def update_total_percent(self):
        """This cannot be called before update_secondary_list"""
        total_percent = 0
        for stat in self.secondary_list:
            total_percent += int(stat['percent_of_max'])
        try:
            self.total_percent = total_percent/len(self.secondary_list)
        except ZeroDivisionError:
            print (self.character)



    def update_secondary_list(self, secondary_json):
        """This cannot be called before create_stat_dic"""
        secondary_dic = {}
        secondary_dic['id'] = secondary_json['stat']['unitStatId']
        secondary_dic['value'] = secondary_json['stat']['statValueDecimal']
        secondary_dic['unscaled_value'] = secondary_json['stat']['unscaledDecimalValue']
        secondary_dic['rolls'] = secondary_json['statRolls']
        
        try:
            secondary_dic['stat'] = self.stat_dic[secondary_dic['id']][0]
            secondary_dic['suffix'] = self.stat_dic[secondary_dic['id']][1]
            secondary_dic['roll_name'] = self.stat_dic[secondary_dic['id']][2]
        except KeyError:
            print (secondary_dic['id'])
            print (secondary_dic['value'])


        if secondary_dic['suffix'] == '%':
            secondary_dic['display_value'] = round(secondary_dic['unscaled_value']/1000000, 2)
        else:
            secondary_dic['display_value'] = round(secondary_dic['value']/10000)




        max_str = secondary_dic['roll_name'] + '_max_roll'
        if int(self.dot) == 5:
            secondary_dic['avg_roll'] = round(float(secondary_dic['display_value'])/secondary_dic['rolls'], 2)
            secondary_dic['max_roll'] = getattr(mstats, max_str)
        elif int(self.dot) == 6:
            increase = getattr(mstats, secondary_dic['roll_name'] + '_increase')
            #secondary_dic['avg_roll'] = round((float(secondary_dic['display_value'])/secondary_dic['rolls'])*increase, 2)

            secondary_dic['max_roll'] = round(getattr(mstats, max_str)*increase,2)
        elif int(self.dot) < 5:
            #print ("Why do you have this mod?")
            #print (self.character)
            secondary_dic['avg_roll'] = round(float(secondary_dic['display_value'])/secondary_dic['rolls'], 2)
            secondary_dic['max_roll'] = getattr(mstats, max_str)


        secondary_dic['avg_roll'] = round(float(secondary_dic['display_value'])/secondary_dic['rolls'], 2)
        min_str = secondary_dic['roll_name'] + '_min_roll'
        secondary_dic['min_roll'] = getattr(mstats, min_str)
        secondary_dic['percent_of_max'] = round((secondary_dic['avg_roll']/secondary_dic['max_roll']) * 100)

        self.secondary_list.append(secondary_dic)


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

def make_call():
        file_name = 'player.json'
        URL = 'https://swgoh.shittybots.me/api/player/'
        ALLY_CODE =  '482764294'
        headers = {'shittybot': config.S_AUTH}
        last_update = []

        final_url = URL + ALLY_CODE
        try:
            print ("making call")
            response = requests.get(final_url, headers=headers, timeout=5)
        except Timeout:
            return
        print (response.status_code)
        
        if response.status_code == 429:
            print ("too many requests")
            return
        elif response.status_code == 200:
            with open(file_name, 'w') as write_file:
                write_file.write(json.dumps(response.json()))
                print ("written")


def data_viewer(file_name):
    """Lets get the mods"""
    #We should probably make of find a dictionary of id:unit
    mod_list = []
    with open(file_name, 'r') as inp:
        dict_list = json.loads(inp.read())

    unitList = dict_list['rosterUnitList']
    for unit in unitList:
        char = Unit(unit)
        for mod in char.mod_list:
            for stat in mod.secondary_list:
                if stat['stat'] == 'Speed':
                    if stat['percent_of_max'] > 95:
                        mod_list.append(mod)
        #print (obj.get_mod_by_shape("Arrow"))

        if unit['id'] == "Roe9iRgfQAGHevY756Eosw":
            yoda = Unit(unit)
        if unit['id'] == 'pwYzbAsMTMCY-lRpr3Lgtw':
            greef = Unit(unit)
    def s_func(mod):
        return mod.total_percent
    out_list = sorted(mod_list, key = s_func)
    out_list.reverse()
    for mod in out_list:
        print (mod)

#    print ("Yoda \n")
#    print (yoda)
#    print ("Greef \n")
#    print (greef)
#

make_call()
mstats = mods.modStats()
data_viewer('player.json')





