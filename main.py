import discord
import openai
import secret


# Discord API setups
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Open Ai API setups
client = openai(
    organization = secret.open_ai_org,
    project = secret.project_id
)

# Placeholder to prove that python scripts run within discord
def reverse_string(input):
    try:
        return(input[::-1])
    except TypeError:
        return("Error with string, unable to reverse")
    
def get_openai_response(input:str) -> float:
    # TODO access openai to call the sentiment analysis function on input
    return

def activate_timeout():
    # TODO activate slow mode in discord
    return

def end_timeout():
    # TODO turn off slow mode in discord
    return

def mood_decay(current_anger: float) -> float:
    # TODO multi threaded argument that decays the anger level over time
    return

current_anger = 0

# constantly running in another thread
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        await current_anger += get_openai_response(message.content)

# Constantly running in one thread
if current_anger > 5:
    activate_timeout
elif current_anger <= 0:
    end_timeout
else:
    mood_decay(current_anger)

client.run(secret.token)