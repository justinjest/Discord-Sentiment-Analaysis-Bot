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
    await channel_name.edit(slowmode_delay=60)
    await channel_name.send("Slowmode activated due to hot heads")

async def end_timeout(channel_name):
    await channel_name.edit(slowmode_delay=0)
    await channel_name.send("Slowmode turned off")
    

def mood_decay(current_anger: float) -> float:
    if current_anger > 0:
        print ("mood decays down")
        anger_tracker(-.1) 
    elif current_anger < 0:
        print ("mood decays up") 
        anger_tracker(.1)
    else:
        current_anger = 0
    return current_anger


# constantly running in another thread
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        # await end_timeout(message.channel)
        return
    else:
        response = get_openai_response(message.content)
        await message.channel.send(get_openai_response(response))
        try: 
            anger_tracker(response)
        except TypeError:
            message.channel.send("Error with message content not interagable.")
        # await activate_timeout(message.channel)

# Function to keep track of a variable, insure it is initialized, and keep it in scope
# Calling this with 0 will allow youto simply pull the value


def anger_tracker(anger_change, current_anger = 5):
    try:
        current_anger += anger_change
        return (current_anger)
    except NameError:
        print ("Name error")

        return (current_anger)
# Constantly running in one thread

def mood_management(current_anger):
    # Really stupid way to make this wait but it is testing rn
    time.sleep(5)
    print (f"Running mood_management, current mood is {current_anger}")
    if current_anger < 5:
        mood_decay(anger_tracker(0))
        # activate_timeout
        mood_management(anger_tracker(0))
    elif current_anger >= 0:
        # end_timeout
        mood_management(anger_tracker(0))
    else:
        mood_decay(anger_tracker(0))
        mood_management(anger_tracker(0))

threading.Thread(target=mood_management, args=(anger_tracker(0),)).start()

client.run(secret.token)