class modStats():
    def __init__(self):
        self.cc_min_roll = 1.125
        self.cc_max_roll = 2.25
        self.cc_increase = 1.04
        self.defense_min_roll = 4
        self.defense_max_roll = 10
        self.defense_increase = 1.63
        self.defenseP_min_roll = .85
        self.defenseP_max_roll = 1.7
        self.defenseP_increase = 2.34
        self.health_min_roll = 214
        self.health_max_roll = 428
        self.health_increase = 1.26
        self.healthP_min_roll =.563
        self.healthP_max_roll = 1.125
        self.healthP_increase = 1.86
        self.offense_min_roll = 23
        self.offense_max_roll = 46
        self.offense_increase = 1.1
        self.offenseP_min_roll = .281
        self.offenseP_max_roll = .563
        self.offenseP_increase = 3.02
        self.potency_min_roll = 1.125
        self.potency_max_roll = 2.25
        self.potency_increase = 1.33
        self.protection_min_roll = 415
        self.protection_max_roll = 830
        self.protection_increase = 1.11
        self.protectionP_min_roll = 1.125
        self.protectionP_max_roll = 2.25
        self.protectionP_increase = 1.33
        self.speed_min_roll = 3
        self.speed_max_roll = 6
        self.speed_increase = 1.03
        self.tenacity_min_roll = 1.125
        self.tenacity_max_roll = 2.25
        self.tenacity_increase = 1.33


        # self.criticalchance = {'min': 1.125, 'max': 2.25}
        # self.defense = {'min': 4, 'max': 10}
        # self.defense_percent = {'min': .85, 'max': 1.7}
        # self.health = {'min': 214, 'max': 428}
        # self.health_percent = {'min': .563, 'max': 1.125}
        # self.offense = {'min': 23, 'max': 46}
        # self.offense_percent = {'min': .281, 'max': .563}
        # self.potency = {'min': 1.125, 'max': 2.25}
        # self.protection = {'min': 415, 'max': 830}
        # self.protection_percent = {'min': 1.125, 'max': 2.25}
        # self.speed = {'min': 3, 'max': 6}
        # self.tenacity = {'min': 1.125, 'max': 2.25}

        self.stat_dic = {}
        self.stat_dic[1] = {'min': 214, 'max': 428} # Health
        self.stat_dic[5] = {'min': 3, 'max': 6} # Speed 
        self.stat_dic[17] = {'min': 1.125, 'max': 2.25} # Potency
        self.stat_dic[18] = {'min': 1.125, 'max': 2.25} # Tenacity
        self.stat_dic[28] = {'min': 415, 'max': 830} # Flat Protection
        self.stat_dic[41] = {'min': 23, 'max': 46} # Flat Offense
        self.stat_dic[42] = {'min': 4, 'max': 10} # Defense
        self.stat_dic[49] = {'min': .85, 'max': 1.7} # Percent Defense
        self.stat_dic[48] = {'min': .281, 'max': .563} # Percent Offense
        self.stat_dic[53] = {'min': 1.125, 'max': 2.25} #Crit Chance
        self.stat_dic[55] = {'min': .563, 'max': 1.125} # Percent Health
        self.stat_dic[56] = {'min': 1.125, 'max': 2.25} # Percent Protection


        self.stat_dic6 = {}
        self.stat_dic6[1] = {'min': 270, 'max': 540} # Health
        self.stat_dic6[5] = {'min': 3, 'max': 6} # Speed 
        self.stat_dic6[17] = {'min': 1.5, 'max': 3} # Potency
        self.stat_dic6[18] = {'min': 1.5, 'max': 3} # Tenacity
        self.stat_dic6[28] = {'min': 460, 'max': 921} # Flat Protection
        self.stat_dic6[41] = {'min': 26, 'max': 51} # Flat Offense
        self.stat_dic6[42] = {'min': 8, 'max': 16} # Defense
        self.stat_dic6[49] = {'min': 1.989, 'max': 3.978} # Percent Defense
        self.stat_dic6[48] = {'min': .85, 'max': 1.7} # Percent Offense
        self.stat_dic6[53] = {'min': 1.175, 'max': 2.35} #Crit Chance
        self.stat_dic6[55] = {'min': 1, 'max': 2} # Percent Health
        self.stat_dic6[56] = {'min': 1.5, 'max': 3} # Percent Protection

        self.criticalchance = {'min': 1.125, 'max': 2.25}
        self.defense = {'min': 4, 'max': 10}
        self.defense_percent = {'min': .85, 'max': 1.7}
        self.health = {'min': 214, 'max': 428}
        self.health_percent = {'min': .563, 'max': 1.125}
        self.offense = {'min': 23, 'max': 46}
        self.offense_percent = {'min': .281, 'max': .563}
        self.potency = {'min': 1.125, 'max': 2.25}
        self.protection = {'min': 415, 'max': 830}
        self.protection_percent = {'min': 1.125, 'max': 2.25}
        self.speed = {'min': 3, 'max': 6}
        self.tenacity = {'min': 1.125, 'max': 2.25}

    def get_stat_details(self, stat, dot):
        if dot == 5:
            return self.stat_dic[stat]
        elif dot == 6:
            return self.stat_dic6[stat]
        elif dot < 5:
            return self.stat_dic[stat]
        
            #return getattr(self, stat)







         



