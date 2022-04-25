import json
import requests
from requests.exceptions import Timeout
import os
import datetime
import time
import re
import discord
from discord.ext import commands, tasks
from asyncio import exceptions
import plotly.express as px
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import helper

class Squad(commands.Cog):
    """This is in beta. It is for helping out with various squads."""
    def __init__(self, bot):
        self.bot = bot
        self.register_file = 'registered_users.json'
        print ('Squad cog initialized')


    @commands.command(name="register")
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
        
