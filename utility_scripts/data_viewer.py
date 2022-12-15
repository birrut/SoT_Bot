import json
import datetime



class Member():
    """ This should take 1 member's json and create a member object"""
    def __init__(self, json):
        self.name = json['playerName']
        self.id = json['playerId']
        #check this do we need to iterate and check that type == 2?
        for item in json['memberContributionList']:
            if item['type'] == 2:
                self.tickets = item['currentValue']
        self.gp = json['galacticPower']
#My Server
num_name = './discord_bot2/data/888611226593136690guild_data.json'
file_name = './discord_bot2/data/888611226593136690.json'


#Guild Server
#num_name = '884464695476625428guild_data.json'
#file_name = '884464695476625428.json'
member_list = []
new_list = []
old_mol = '0sxqmAAQS7mAa9KrkUg07Q'
new_mol = '71HUHwI7RZ2Pt6dZ2b8w3w'
new_dict = {}
#he joine on the 12, so we will delet 11 and before
join_date = datetime.datetime(2022, 1, 12)
with open(file_name, 'r') as guild_file:
    guild_data = json.loads(guild_file.read())
    print (len(guild_data))

with open (num_name, 'r') as num_file:
    id_lookup = json.loads(num_file.read())

day = id_lookup[-1]
for member in day['memberList']:
    member_list.append(Member(member))

#print (member_list)

for member in guild_data[-1]:
    for mem_object in member_list:
        if member == mem_object.name:
           new_dict[mem_object.id] =  [mem_object.name, guild_data[-1][member]]
            
    new_dict ['date'] = guild_data[-1]['date']
    new_dict ['guild name'] = guild_data[-1]['guild name']
    new_dict ['total'] = guild_data[-1]['total']
    new_dict ['average'] = guild_data[-1]['average']

print (new_dict)
guild_data.pop()
guild_data.append(new_dict)

#for day in guild_data:
#    new_day = {}
#    #print (day)
#    for member in member_list:
#        if member.name in day:
#            new_day[member.id] = [member.name, day[member.name]]
#    new_day['date'] = day['date']
#    new_day['guild name'] = day['guild name']
#    new_day['total'] = day['total']
#    new_day['average'] = day['average']
#    new_list.append(new_day)


with open(num_name, 'w') as out_file:
    print (len(guild_data))
    out_file.write(json.dumps(guild_data))




#for day in guild_data:
#    for member in day:
#        print (member)
#


#member_list = guild_data[7]['memberList']
#print (len(member_list))
#name_list = []
#for member in member_list:
#    name_list.append(member['playerName'])
#
#print (len(name_list))
#print (name_list)
