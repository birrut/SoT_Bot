import json
import requests
import mods
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
import config

color_dict = {1:'Grey', 2:'Green', 3:'Blue', 4:'Purple', 5:'Gold'}

class Mod():
    def __init__(self, mod_json):
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


        self.update_total_percent()

    def __repr__(self):
        out = self.character
        out += f'\nLevel: {self.level} Color: {color_dict[self.tier]} Dots: {self.rarity}, Set: {self.set}, {self.shape} t_p: {self.total_percent}%\n'
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
            except:
                print ('error', second)
                #print (f"Don't know this id: {second['id']}")

            #out += f" Min roll: {second['min_roll']} Avg roll: {second['avg_roll']} Max roll: {second['max_roll']}"
            #out += f"\nPercent of max: {second['percent_of_max']}"
        out +='\n'

        return out


    def update_total_percent(self):
        """This cannot be called before update_secondary_list"""
        total_percent = 0
        for stat in self.secondary_list:
            total_percent += float(stat['percent_of_max'])
        try:
            self.total_percent = total_percent/len(self.secondary_list)
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

    def OLDupdate_secondary_list(self, secondary_json):
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
            print ('up here')
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
    return mod.total_percent

if __name__ == "__main__":
    m_json = make_call(482764294)
    mod_list = []
    for mod in m_json['mods']:
        m = Mod(mod)
        mod_list.append(m)
        if m.character == "POGGLETHELESSER":
            pass
            # print(m)
    sorted_list = sorted(mod_list, key=order_mods)
    sorted_list.reverse()
    for mod in sorted_list[:10]:
        print(mod)

