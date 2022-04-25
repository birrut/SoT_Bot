import json
import datetime

in_file = '888611226593136690guild_data.json'
#in_file = '888611226593136690.json'

with open(in_file, 'r') as in_data:
    data = json.loads(in_data.read())


#for day in data:
#    d_date = datetime.datetime.fromisoformat(day['date'])
#    if d_date.hour == 1:
#        print (d_date)
#        new_date = d_date - datetime.timedelta(hours=7)
#        ind = data.index(day)
#        data[ind]['date'] = str(new_date)

for day in data:
    d_date = datetime.datetime.fromisoformat(day['date'])
    new_date = d_date + datetime.timedelta(hours=7)
    print (d_date, new_date)
    ind = data.index(day)
    data[ind]['utc time'] = str(new_date)

#with open(in_file, 'w') as out_file:
#    out_file.write(json.dumps(data))


