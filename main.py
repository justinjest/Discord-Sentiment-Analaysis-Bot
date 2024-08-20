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
# From GPT I got the idea to use classes to track things outside of 
# the scope of a function
class AngerTracker:
    def __init__(self):
        self.current_anger = 0.0
    
    def track(self, anger_change: float) -> float:
        self.current_anger += anger_change
        self.current_anger = round(self.current_anger, 1)
        return self.current_anger

tracker = AngerTracker()

class SlowMode:
    def __init__(self):
        self.slow_mode = False
        self.latch = False
    def toggle(self, slow_mode_on: bool):
        self.slow_mode = slow_mode_on
slow = SlowMode()

        
# mood functions
def mood_decay() -> float:
    # print ("Mood decay active")
    if tracker.current_anger > -4:
        # print ("mood decays down")
        tracker.track(-.1) 
    elif tracker.current_anger < 0:
        # print ("mood decays up") 
        tracker.track(.1)
    return tracker.current_anger

# Constantly running in one thread
def mood_management():
    print (f"Running mood_management, current mood is {tracker.current_anger}")
    # Really stupid way to make this wait but it is testing rn
    time.sleep(60) 
    mood_decay()
    mood_management()

def slow_mode_sensor():
    print(f"Slow_mode_sensor is at {tracker.current_anger}")
    if tracker.current_anger <= -4:
        slow.toggle(True)
    elif tracker.current_anger >= 0:
        slow.toggle(False)
    time.sleep(10) 
    slow_mode_sensor()

# OpenAI functions
def get_openai_response(input:str) -> float:
    # TODO improve prompt to something slightly cleaner
    completion = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content":"You are a sentiment analyzer. Your task is to evaluate the tone of a message and provide a score between -1 and 1 based on its emotional content. Follow these guidelines: Score of 1: Assign this to messages that are very helpful, positive, or happy. Score between 0 and 1: Assign this to messages that are somewhat helpful or mildly positive. Score of 0: Assign this to neutral messages, which are neither positive nor negative. Score between -1 and 0: Assign this to messages that are somewhat angry, frustrated, or mildly negative. Score of -1: Assign this to messages that are very angry, frustrated, or rude. Your response should be a single floating-point number, with no additional text."},
            {
                "role": "user",
                "content": input,
                "temperature": "0.03"
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
    

# constantly running in another thread
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):  
    helpful_messages = {"$mood": f"Current mood is {tracker.current_anger}",
                        "$help": "I help turn the server into slow mode when people get angry. Use $mood for current mood"}
    if message.author == client.user:
        return
    else:
        if slow.latch != slow.slow_mode:
            print(f"Latch is {slow.latch}, toggle is {slow.slow_mode}")
            slow.latch = slow.slow_mode
            if slow.slow_mode == True:
                await activate_timeout(message.channel)
            elif slow.slow_mode == False:
                await end_timeout(message.channel) 
                
        for key in helpful_messages:
            if message.content == key:
                await message.channel.send(helpful_messages[key])
            return
        response = get_openai_response(message.content)
        try: 
            tracker.track(float(response))
            print(f"New current_anger is {tracker.current_anger}")
        except TypeError:
            await message.channel.send("Error with message content not interagable.")

if __name__ == '__main__':
    threading.Thread(target=mood_management).start()
    threading.Thread(target=slow_mode_sensor).start()
    client.run(secret.token)