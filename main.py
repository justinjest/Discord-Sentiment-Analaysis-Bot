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
# Keeps track of anger and is critical function for this program
# From GPT
class AngerTracker:
    def __init__(self):
        self.current_anger = 0
    
    def track(self, anger_change):
        self.current_anger += anger_change
        return self.current_anger

tracker = AngerTracker()

class slowMode:
    def __init__(self):
        self.slow_mode = False

    def slow_mode_change(self, slow_mode_on):
        self.slow_mode = slow_mode_on

slow = slowMode()

        
# mood functions
def mood_decay(current_anger: float) -> float:
    # print ("Mood decay active")
    if tracker.current_anger > 0:
        # print ("mood decays down")
        tracker.track(-.1) 
    elif tracker.current_anger < 0:
        # print ("mood decays up") 
        tracker.track(.1)
    return current_anger

# Constantly running in one thread
def mood_management(current_anger):
    print (f"Running mood_management, current mood is {current_anger}")
    # Really stupid way to make this wait but it is testing rn
    time.sleep(60)
    if current_anger < -4:
        print ("Mood below -4")
        mood_decay(tracker.current_anger)
        slow.slow_mode_change(True)
        mood_management(tracker.current_anger)
    elif current_anger >= 0:
        mood_decay(tracker.current_anger)
        slow.slow_mode_change(False) 
        mood_management(tracker.current_anger)
    else:
        mood_decay(tracker.current_anger)
        mood_management(tracker.current_anger)

# OpenAI functions
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

# Discord functions
async def activate_timeout(channel_name):
    print ("Timeout activated")
    await channel_name.edit(slowmode_delay=60)
    await channel_name.send("Slowmode activated due to hot heads")

async def end_timeout(channel_name):
    print ("Timeout ended")
    await channel_name.edit(slowmode_delay=0)
    await channel_name.send("Slowmode turned off")
    

# constantly running in another thread
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        response = get_openai_response(message.content)
        await message.channel.send(get_openai_response(response))
        try: 
            tracker.track(float(response))
            print(f"New current_anger is {tracker.current_anger}")
        except TypeError:
            await message.channel.send("Error with message content not interagable.")
    print (f"Slow mode is currently {slow.slow_mode}")
    if slow.slow_mode == True:
        await activate_timeout(message.channel)
    elif slow.slow_mode == False:
        await end_timeout(message.channel)


threading.Thread(target=mood_management, args=(tracker.current_anger,)).start()
client.run(secret.token)