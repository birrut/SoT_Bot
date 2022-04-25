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
                if key not in non_count_list:
                    num_list.append(d[key])
            average = round(sum(num_list)/len(num_list))
            total = sum(num_list)
            d['total'] = total
            d['average'] = average
            out_dictionary_list.append(d)
    return out_dictionary_list
    
        
file_name = '884464695476625428.json'
new_data = rewrite(file_name)

with open(file_name, 'w') as output:
    output.write(json.dumps(new_data))
            


