import discord
from discord.ext import commands
import requests
import aiohttp


import os
from dotenv import load_dotenv
load_dotenv()
WEATHER_URL = os.getenv("WEATHER_URL")


class weather(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.url = WEATHER_URL
    
    @commands.command()      
    async def emoji(self, ctx: commands.Context, emoji: discord.Emoji):
        # emoji_url = emoji.url
        # embed = discord.Embed(title=f"{emoji.name}", color=0x0cdfd1)
        # embed.set_image(url=emoji_url)
        # await ctx.reply(embed=embed)    
        await ctx.reply(emoji.url)  
        # await ctx.reply(emoji.id) 


    @commands.command()
    async def w(self, ctx: commands.Context):
        data = requests.get(self.url)   # 取得 JSON 檔案的內容為文字
        data_json = data.json()    # 轉換成 JSON 格式
        location = data_json['records']['location']
        for i in location:
            time = i['weatherElement'][0]['time'][0]['startTime']
            city = i['locationName']    # 縣市名稱
            wx8 = i['weatherElement'][0]['time'][0]['parameter']['parameterName']    # 天氣現象
            maxt8 = i['weatherElement'][4]['time'][0]['parameter']['parameterName']  # 最高溫
            mint8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最低溫
            ci8 = i['weatherElement'][3]['time'][0]['parameter']['parameterName']    # 舒適度
            pop8 = i['weatherElement'][1]['time'][0]['parameter']['parameterName']   # 降雨機率
            if city == "臺北市":
                embed=discord.Embed(title=f"{city} | 12小時天氣預報", description=f"{wx8}", color=0x0cdfd1)
                embed.add_field(name="溫度", value=f"`{mint8}`~`{maxt8}`˚C   ", inline=True)
                #embed.add_field(name="最低溫", value=f"`{mint8}`", inline=True)
                embed.add_field(name="降雨機率", value=f"`{pop8}` %   ", inline=True)
                embed.add_field(name="舒適度", value=f"`{ci8}`", inline=True)
                embed.set_footer(text=f"Last updated: {time}")
                await ctx.reply(embed=embed)
                # await ctx.reply(f'{city}未來 12 小時{wx8}，最高溫 {maxt8} 度，最低溫 {mint8} 度，降雨機率 {pop8} % 舒適度 {ci8}。')
        
    

async def setup(bot: commands.Bot):
    await bot.add_cog(weather(bot))