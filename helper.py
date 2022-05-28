import datetime
import math

def get_growth_list(gp_list):
    """takes a list of gp and returns list of growth"""
    out_list = []
    for day_index in range(1, len(gp_list)):
        out_list.append(gp_list[day_index] - gp_list[day_index - 1])

    return out_list

def binomial(n,x,p):
    """Binomial probability function."""
    try:
        P = (math.factorial(n)/(math.factorial(x)*math.factorial(n-x)))*pow(p,x)*pow((1-p), n-x)
    except ValueError as e:
        # print(n,x,p,e)
        P=0
    return P

def cumulative(n, x, p=.25, digits=2):
    """n is remaining number of hits, x is number to 5 speed hits,
    p is .25"""
    # print(f"Hits remaining: {n}, Speed hits: {5-x}")
    poss_list = []
    for option in range(x):
        # print(option)
        poss_list.append(binomial(n, option, p))
    # if x == 1:
        #print(f"{n}, {x}, {1 - sum(poss_list)}")
    return round(1 - sum(poss_list),2)


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


    def create_gp_lists(self, json_list, days):
        """This takes a json list, just as it comes from the file and creates gp history list and a date list"""
        #days is the number of days to add to the lists
        self.date_list = []
        self.gp_history = []
        for day in json_list[-days:]:
            date = datetime.datetime.fromisoformat(day['date'])
            if date not in self.date_list:
                self.date_list.append(date)
            else:
                print("We should never be here, right")
            for member in day['memberList']:
                if self.id == member['playerId']:
                    self.gp_history.append(member['galacticPower'])
        while len(self.gp_history) < days:
            self.gp_history.insert(0, self.gp_history[0])
            print ('adding padding to {}, length is now {}.'.format(self.name, len(self.gp_history)))
        self.growth_list = get_growth_list(self.gp_history)
        #this is for growth only. I don't think this should be here
        self.date_list.pop(0)


    def change_to_weekly(self, num_weeks):
        """This should only be called after create_gp_lists. This will replace self.growth_list with the weekly growth list"""
        weekly_list = []
        def n_list(week):
            #weekly_list.insert(0, sum(week)/len(week))
            weekly_list.insert(0, week[6])
        temp_list = self.gp_history.copy()
        #This  removes initial day, which is only used for growth start
        initial = temp_list.pop(0)
        while len(temp_list)%7 !=0:
            temp_list.insert(0,0)

        while len(temp_list) != 0:
            n_list(temp_list[-7:])
            temp_list = temp_list[:-7]
        weekly_list.insert(0, self.gp_history[0])
        self.growth_list = get_growth_list(weekly_list)

