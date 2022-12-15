import json

def rewrite(f):
    out_dictionary_list = []
    non_count_list = ['date', 'guild name', 'average', 'total']
    with open(f, 'r') as input_file:
        d_list = json.loads(input_file.read())
        for d in d_list:
            num_list = []
            print ('here')
            for key in d:
                average = round(sum(num_list)/len(num_list))
                total = sum(num_list)
            d['total'] = total
            d['average'] = average
            out_dictionary_list.append(d)
    return out_dictionary_list

def add_600(f):
    out_dictionary_list = []
    non_count_list = ['utc time', 'date', 'guild name', 'average', 'total']
    with open(f, 'r') as input_file:
        d_list = json.loads(input_file.read())
        print(len(d_list))
        for d in d_list:
            num_list = []
            num_600 = 0
            for key in d:
                if key not in non_count_list:
                    #print(d[key])
                    num_list.append(d[key][1])
                    if d[key][1]==600:
                        num_600+=1

            d['num_600'] = num_600
            out_dictionary_list.append(d)
    print(len(out_dictionary_list))
    return out_dictionary_list

#SOT        
file_name = './discord_bot2/data/884464695476625428.json'
#MyServer
#file_name = './discord_bot2/data/888611226593136690.json'
#add_600(file_name)
#new_data = rewrite(file_name)

new_data = add_600(file_name)
#print(new_data)
#with open(file_name, 'w') as output:
#    output.write(json.dumps(new_data))
            


