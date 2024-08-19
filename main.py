import discord
from openai import OpenAI
import secret
import threading
import time
# Discord API setups
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Open Ai API setups    
openai_client = OpenAI(
    api_key = secret.project_id
)

# Placeholder to prove that python scripts run within discord
def reverse_string(input):
    try:
        return(input[::-1])
    except TypeError:
        return("Error with string, unable to reverse")
    
def get_openai_response(input:str) -> float:
    # TODO improve prompt to something slightly cleaner
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "You will rank all messages you receive with a score from -1 to 1. You will rank helpful, or happy messages with a score of 1. You will rank angry, frustrated, or rude messages with a score of -1. You will rank it 0 if a message is neither. You will rank messages between 1 and 0 if they are somewhat helpful, you will rank a message between 0 and -1 if it is somewhat angry. You will provide no response except for a single float.",
            },
        ],
    )
    return (completion.choices[0].message.content)

async def activate_timeout(channel_name):
    # TODO activate slow mode in discord
    await channel_name.edit(slowmode_delay=60)
    await channel_name.send("Slowmode activated due to hot heads")

async def end_timeout(channel_name):
    # TODO turn off slow mode in discord
    await channel_name.edit(slowmode_delay=0)
    await channel_name.send("Slowmode turned off")
    

def mood_decay(current_anger: float) -> float:
    if current_anger > 0:
        current_anger -= .1
    elif current_anger < 0: 
        current_anger += .1
    else:
        current_anger = 0
    return current_anger

current_anger = 0

# constantly running in another thread
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        await end_timeout(message.channel)
    else:
        response = get_openai_response(message.content)
        await message.channel.send(get_openai_response(response))
        try: 
            current_anger += response 
        except TypeError:
            message.channel.send("Error with message content not interagable.")
        await activate_timeout(message.channel)

# Constantly running in one thread
def mood_management(current_anger):
    # Really stupid way to make this wait but it is testing rn
    time.sleep(60)
    if current_anger < 5:
        mood_decay(current_anger)
        activate_timeout
        mood_management(current_anger)
    elif current_anger >= 0:
        end_timeout
        mood_management(current_anger)
    else:
        mood_decay(current_anger)
        mood_management(current_anger)

threading.Thread(target=mood_management, args=(current_anger,)).start()

client.run(secret.token)