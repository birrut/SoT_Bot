import json
import datetime



def remove_day(f, date):
    out_dictionary_list = []
    #print (date)
    with open(f, 'r') as input_file:
        d_list = json.loads(input_file.read())
        print ("Original Length: ", len(d_list))
        for d in d_list:
            if date == datetime.datetime.fromisoformat(d['date']).date():
                print ("Removing: ", datetime.datetime.fromisoformat(d['date']).date())
            else:
                out_dictionary_list.append(d)
    return out_dictionary_list           
        





#Main
file_name = '884464695476625428.json'
#MyServer
#file_name = '888611226593136690.json'

#current = datetime.datetime.now()
#today = current.date()
input_date = '2021-12-29'
today = datetime.datetime.fromisoformat(input_date).date()
print ('input date: ', today)
new_list = remove_day(file_name, today)
print ("End Length: ", len(new_list))
with open (file_name, 'w') as output:
    output.write(json.dumps(new_list))
