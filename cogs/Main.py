import discord
from discord.ext import commands, tasks
import asyncio
from PIL import Image

import random
import datetime
import google.generativeai as genai
import openai

import os
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
CHATGPT_KEY = os.getenv("CHATGPT_KEY")

def safety_level(prob):
    if prob == 0:
        return "HARM_PROBABILITY_UNSPECIFIED"
    elif prob == 1:
        return "NEGLIGIBLE"
    elif prob == 2:
        return "LOW"
    elif prob == 3:
        return "MEDIUM"
    elif prob == 4:
        return "HIGH"
def chat_with_pure_model(user_input):
    genai.configure(api_key=GEMINI_KEY)

    # Set up the model
    generation_config = {
      "temperature": 0.75,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 2048,
    }
    safety_settings = [
        {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]
    

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings
                                  )
    response = model.generate_content(user_input)

    if response.prompt_feedback.safety_ratings[0].probability>=3:
        return f"**HOU!** 此問題因為煽情露骨被阻擋  `程度:{safety_level(response.prompt_feedback.safety_ratings[0].probability)}`"
    if response.prompt_feedback.safety_ratings[1].probability>=3:
        return f"**HOU!** 此問題因為仇恨言論被阻擋  `程度:{safety_level(response.prompt_feedback.safety_ratings[1].probability)}`"
    if response.prompt_feedback.safety_ratings[2].probability>=3:
        return f"**HOU!** 此問題因為騷擾內容被阻擋  `程度:{safety_level(response.prompt_feedback.safety_ratings[2].probability)}`"
    if response.prompt_feedback.safety_ratings[3].probability>=3:
        return f"**HOU!** 此問題因為危險內容被阻擋  `程度:{safety_level(response.prompt_feedback.safety_ratings[3].probability)}`"

    # if response.candidates == []:
    #     return f"{response.prompt_feedback}\n也就是說你的問題太兇ㄌ"
    return response.text

def chat_image(user_input_image):
    genai.configure(api_key=GEMINI_KEY)

    model = genai.GenerativeModel('gemini-pro-vision')
    #response = model.generate_content(user_input_image)
    response = model.generate_content(["What may this image represent? Give me the short Answer.", user_input_image])
    return response.text

def chat_image2(user_input_text,user_input_image):
    genai.configure(api_key=GEMINI_KEY)

    model = genai.GenerativeModel('gemini-pro-vision')
    #response = model.generate_content(user_input_image)
    response = model.generate_content([user_input_text, user_input_image])
    return response.text

def chat_gpt(user_input):
    client = openai.OpenAI(api_key=CHATGPT_KEY,base_url="https://api.chatanywhere.tech/v1")
    response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = [{'role':'user','content': user_input}],
            temperature = 1
    )
    return response.choices[0].message.content


# 定義名為 Main 的 Cog
class Main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.cron_task.start()



    # 前綴指令
    @commands.command()
    async def Hello(self, ctx: commands.Context):
        await ctx.reply("Hello, world!")
        

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.content == "Hello":
            await message.channel.send("Hello, world!")
            

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if message.author == self.bot.user:  # Ignore messages from the bot itself
    #         return
    #     if message.content.lower().startswith("chat "):  # Check if the message starts with "chat "
    #         user_input = message.content[5:]  # Extract the user input
    #         output = chat_with_pure_model(user_input)  # Process the input
    #         await message.channel.send(output)  # Send the output to the same channel

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:  # Ignore messages from the bot itself
            return
        
        if message.content.lower().startswith("chatgpt "):  # Check if the message starts with "chat "
            user_input = message.content[8:]  # Extract the user input
            output = chat_gpt(user_input)  # Process the input
            await message.reply(output)  # Send the output to the same channel
            if output == None:
                await message.reply("Fail to Response") 
            
            
        if message.attachments and "a wild countryball appeared!" in message.content.lower():
            for attachment in message.attachments:
                if attachment.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    # Save the image locally if you want to
                    await attachment.save(f'images.png')
                    # Convert the image to bytes
                    img = Image.open('images.png')
                    # image_bytes = await attachment.read()
                    # Call the chat_image function with the image bytes
                    # response_text = chat_image(image_bytes)
                    response_text = chat_image(img)

                    # Send the response back to Discord
                    await message.channel.send(response_text)
        
        elif message.attachments and message.content.lower().startswith("chat "):
            for attachment in message.attachments:
                if attachment.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    await attachment.save(f'images2.png')
                    img = Image.open('images2.png')
                    response_text = chat_image2(message.content[5:],img)

                    # Send the response back to Discord
                    await message.reply(response_text)
                else:
                    await message.reply("窩看不懂")

        elif message.content.lower().startswith("chat "):  # Check if the message starts with "chat "
            user_input = message.content[5:]  # Extract the user input
            output = chat_with_pure_model(user_input)  # Process the input
            if output.startswith("**HOU!**") :
                embed=discord.Embed(title="HOU!", description="你輸入了髒東東 <:www:990307047625068634>", color=0xe60f0f)
                embed.add_field(name="原因", value=f"{output[14:18]}", inline=True)
                embed.add_field(name="程度", value=f"{output[27:-1]}", inline=True)
                embed.set_footer(text="到底為什麼要花時間寫這個")
                await message.reply(embed=embed)
            else:
                await message.reply(output)  # Send the output to the same channel
        

    # 復誦訊息
    @commands.command()
    async def say(self, ctx,*, msg):
        await ctx.message.delete()
        await ctx.send(msg)

    #傳送訊息至特定頻道
    # @commands.command()
    # async def saych(self, ctx,*, msg):
    #     # await ctx.message.delete()
    #     channel_id = msg[:19]  # 你的目标频道的ID 1216041908158206012
    #     channel = self.bot.get_channel(channel_id)
    #     await ctx.send(channel_id)
    #     await ctx.send(channel.id)
    #     await channel.send(msg)
    @commands.command()
    async def saych(self, ctx, channel_id: int, *, message):
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            await ctx.send("Invalid channel ID or I don't have permission to send messages there.")
    @commands.command(name='get_icon')
    async def get_icon(self, ctx):
        #await ctx.send("a")
        server = ctx.guild
        #await ctx.send(server)
        if server.icon:
            await ctx.send(f"Server icon: {server.icon}")
        else:
            await ctx.send("This server doesn't have an icon.")
            


    # 讀取圖片訊息
    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #     if message.attachments:
    #         attachment = message.attachments[0]
    #         await message.channel.send("detect picture")
    #         #await message.channel.send(attachment.height,attachment.width,"\n",attachment.size,"\n",attachment.filename,"\n",attachment.description)
    #         await message.channel.send(
    #             f"Width: {attachment.width}\n"
    #             f"Height: {attachment.height}\n"
    #             f"Size: {attachment.size}\n"
    #             f"Filename: {attachment.filename}\n"
    #             f"Description: {attachment.description}"
    #         )
    #         #await message.channel.send(attachment.url)
    #         #width, height = await self.get_image_dimensions(attachment)
    #         #await message.channel.send(f"Width: {width}, Height: {height}")

    # 固定時間傳送訊息
    # def cog_unload(self):
    #     self.cron_task.cancel()
    # @tasks.loop(minutes=5)
    # async def cron_task(self):
    #     channel_id = 1216041908158206012  # 你的目标频道的ID 1216041908158206012
    #     channel = self.bot.get_channel(channel_id)
    #     messages = [
    #         'hou',
    #         'meow',
    #         '胖',
    #         'spawn',
    #         '孵'
    #     ]

    #     if channel:
    #         random_message = random.choice(messages)
    #         await channel.send(random_message)

'''
    async def get_image_dimensions(self, attachment: discord.Attachment):
        try:
            # Open the image using PIL
            with Image.open(await attachment.read()) as img:
                width, height = img.size
                return width, height
        except Exception as e:
            await message.channel.send("error")
            return None, None
'''


            
# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(Main(bot))


