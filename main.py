import discord
import openai
import secret

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def reverse_string(input):
    try:
        return(input[::-1])
    except TypeError:
        return("Error with string, unable to reverse")
    
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        await message.channel.send(reverse_string(message.content))

client.run(secret.token)