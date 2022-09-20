import json
import requests
import discord
from discord.ext import commands, tasks
# import plotly.express as px
# import helper


class Character():
    """This stores the data for one character"""
    def __init__(self, in_json):
        self.json = in_json['data']
        self.name = self.json['name']
        self.gear_level = self.json['gear_level']
        self.level = self.json['level']
        self.power = self.json['power']
        self.rarity = self.json['rarity']
        self.strength = self.json['stats']['2']
        self.agility = self.json['stats']['3']
        self.tactics = self.json['stats']['4']
        self.health = self.json['stats']['1']
        #self.protection = self.json['stats']['28']
        self.speed =  self.json['stats']['5']
        self.get_categories()
        self.get_omicron()
        self.get_zeta_list()




    def __repr__(self):
        out = f"{self.name}: {self.gear_level} Speed: {self.speed}"
        try:
            for cat in self.categories:
                out += f"{cat},"
        except AttributeError:
            print ("HELP!!!", self.name)
        return out

    def get_categories(self):
        with open('data/char_list.json', 'r') as chars:
            char_list = json.loads(chars.read())
            for char in char_list:
                if char['name'] == self.name:
                    self.categories = char['categories']
    def get_omicron(self):
        self.omicron = False
        omicron = self.json['omicron_abilities']
        for ability in self.json['ability_data']:
            #This only works for characters with 1 omicron right now
            if len(omicron) > 0:
                if omicron[0] == ability['id']:
                    self.omicron = ability['has_omicron_learned']

    def get_zeta_list(self):
        self.zeta_list = []
        #possible_zetas = self.json['zeta_abilities']
        for ability in self.json['ability_data']:
            if ability['is_zeta']:
                if ability['has_zeta_learned']:
                    self.zeta_list.append(ability)
        #print(self.zeta_list)



class Squad(commands.Cog):
    """This is in beta. It is for helping out with various squads."""

    def __init__(self, bot):
        self.bot = bot
        self.register_file = 'data/users.json'
        print('Squad cog initialized')

    #@commands.command(name="register")
    async def register_user(self, ctx, user_id):
        guild = ctx.message.guild.id
        member = str(cts.message.author)
        if len(user_id) == 9 or len(user_id) == 11:
            try:
                int_id = int(user_id)
            except ValueError:
                try:
                    user_id.replace('-', '')
                    int_id = int(user_id)
                except ValueError:
                    await ctx.send("That is not a valid user id. Please specify a user id in the form xxxxxxxxx or xxx-xxx-xxx")
                    return
        else:
            await ctx.send("That is not a valid user id. Please specify a user id in the form xxxxxxxxx or xxx-xxx-xxx")
            return
        
        with open(self.register_file, 'r') as reg:
            server_list = json.loads(reg.read())
        

        with open(self.register_file, 'w') as reg:
            reg.write(json.dumps(write_list))

    @commands.command(name="bh")
    async def bh(self, ctx, ally_code_str=None):
        """Info about your bounty hunter squad"""
        try:
            ally_code = int(ally_code_str)
        except TypeError:
            ally_code = None

        GA_dic = {}
        normal_dic = {}
        with open(self.register_file, 'r') as user_file:
            user_list = json.loads(user_file.read())

        if not ally_code:

            ally_code = None 
            for user in user_list:
                if str(ctx.author.id) in user:
                    ally_code = user[str(ctx.author.id)]
        if ally_code == None:
            await ctx.send("You are not registered. Please run $register 123123123")
        
        m_json = make_call(ally_code)
        character_list = []
        for char in m_json['units']:
            ch = Character(char)
            character_list.append(ch)
        bh_list = []
        find_list = ['Greef Karga', 'Bossk', 'The Mandalorian', 'Zam Wesell']
        z_omi = False
        z_omi_speed = 0
        G_percent = 0
        mando_percent = 0
        mando_zeta = False
        for char in character_list:
            if char.name in find_list:
                bh_list.append(char)
            if char.name == 'Zam Wesell':
                if char.omicron:
                    z_omi = True
                    z_omi_speed = char.speed * 1.2
            if char.name == 'The Mandalorian':
                if len(char.zeta_list) > 0:
                    mando_zeta = True

        
        out1 = ''
        out2 = ''
        for char in bh_list:
            #need to check for mando's zeta
            if char.name == "Greef Karga":
                greef_speed = char.speed + z_omi_speed*.2
                greef_speed_reg = char.speed
                if mando_zeta:
                    G_percent = (char.speed + z_omi_speed*.2)/.85
                    G_percent_reg = char.speed/.85
                else:
                    G_percent = greef_speed
                    G_percent_reg = greef_speed_reg
            if char.name == "The Mandalorian":
                mando_percent = (char.speed + z_omi_speed*.2)/.7
                mando_percent_reg = char.speed/.7
            out1 += f"{char.name}: {char.speed}\n"
            #out2 += f"{char.name} base speed: {char.speed}\n"

            if z_omi:
                if char.name != 'Zam Wesell':
                    out2 += f"{char.name}: {char.speed + z_omi_speed*.2}\n"
                else:
                    out2 += f"{char.name}: {z_omi_speed}\n"



        #out of GA
        max_mando = (G_percent_reg - 1)*.7
        if G_percent_reg > mando_percent_reg:
            out1 += f"\n You should get insta kill on Mando's first turn. You could increase his speed to  {round(max_mando)}"
        else:
            out1 += f"\nTry lowering mando to {max_mando}, or increasing Greef's speed"
        out1 += f"\n As long as your opponet doesn't stop TM gain, and doesn't gain turn meter from your attacks, you should be able to out run anybody slower than {greef_speed_reg}"

        #in GA
        max_mando = (G_percent - 1)*.7
        if  z_omi:
            #somethng is wrong with this
            max_mando = max_mando/1.2
            print(G_percent, ' > ', mando_percent)
        if G_percent > mando_percent:
            out2 += f"\n You should get insta kill on Mando's first turn. You could increase his base speed to {round(max_mando)}"
        else:
            out2 += f"\nTry lowering mando to {max_mando}, or increasing Greef's speed"

        out2 += f"\n As long as your opponet doesn't stop TM gain, and doesn't gain turn meter from your attacks, you should be able to out run anybody slower than {greef_speed}"


        #Create and send embeds
        emb1 = discord.Embed(title='Outside of GA', description=out1, color=discord.Color.blue())
        emb2 = discord.Embed(title='Grand Arena', description=out2, color=discord.Color.blue())

        emb1.set_thumbnail(url='attachment://bot.png')
        emb2.set_thumbnail(url='attachment://bot.png')
        image = discord.File('bot.png', filename='bot.png')
        await ctx.send(file=image, embed=emb1)
        image = discord.File('bot.png', filename='bot.png')
        await ctx.send(file=image, embed=emb2)


def make_call(player_id):
    url = f'https://swgoh.gg/api/player/{str(player_id)}'
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
        
