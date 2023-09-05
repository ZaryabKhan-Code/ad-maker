from flask import *
import openai
from flask_login import *
import requests
from model.oauth import *

bot = Blueprint('bot', __name__)
openai.api_key = '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'



def generate_initial_response(time_of_day, current_user):
    instructions = "Please give a greeting to the users."
    prompt = f"You are an efficient assistant. Your job is to say, Good {time_of_day} {current_user}. Give a greeting to the users according to their time frame. You are the ad maker assistant. You can help the users create ads for their business, etc."
    thePrompt = [{"role": "system", "content": prompt}, {"role": "assistant", "content": instructions}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=thePrompt,
        )
        generated_response = response['choices'][0]['message']['content']
    except openai.error.OpenAIError:
        generated_response = f"Hello! I'm here to assist you with your ACA questions."
    return generated_response

from datetime import datetime, time

def get_time_of_day():
    current_time = datetime.now().time()
    if current_time < time(12, 0):
        return "morning"
    elif current_time < time(17, 0):
        return "afternoon"
    else:
        return "evening"

@bot.route('/bot')
def index():
    time_of_day = get_time_of_day()
    initial_message = generate_initial_response(time_of_day, current_user.name)
    return jsonify({'initial_message': initial_message})



@bot.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('user_message')

    user_memory = ChatMemory(user_id=current_user.id, role="user", content=user_message)
    db.session.add(user_memory)
    db.session.commit()

    user_memory_history = ChatMemory.query.filter_by(user_id=current_user.id).all()

    memory = [{"role": message.role, "content": message.content} for message in user_memory_history]

    user_prompt = f"""You are a helpful assistant for <name: {current_user.name} and email: {current_user.username}> with a specialty in helping a user create high converting ads. Your process is summarized as follows ...


How to Create High-Converting Ads: A Step-by-Step Framework

 

1. Clearly Identify Your Objective

 

Be very specific in defining what you want the ad to accomplish. Do you want to generate leads for your sales team? Get prospects to purchase directly? Build general brand awareness? The objective will inform metrics like ideal CPA and CPC. It also focuses your targeting and messaging.

 

2. Research and Understand Your Audience

 

Your ad is useless if seen by the wrong people. Do in-depth research of your target demographics. Look beyond basic stats at their motivations and values. What messaging will appeal to them? What visuals will grab their attention? The better you know them, the better your ads will convert.

 

3. Strategically Choose Where to Place Ads

 

Research where your target audience spends time online and offline. Look at direct competitors - where are they advertising successfully? Some options: Search, Social, Display, Native, TV, Radio, Print. Choose platforms and specific sites that maximize relevant reach.

 

4. Craft a Persuasive Ad Copy Framework

 

Your copy needs 3 core components - hook, value, CTA:

 

- Hook their attention immediately (4-5 sec) with labels, questions, curiosity gaps.

 

- Show value by making your offering's benefits massive and costs tiny from multiple perspectives.

 

- Direct them clearly on what to do next with a clear, simple call to action.

 

5. Develop Captivating Ad Creatives

 

Complement your copy with visuals, sounds and contrast that accentuate your messaging. Show don't just tell. Test different images, people, settings, situations that appeal to your audience.

 

6. Send Traffic to a Focused Landing Page

 

Don't send them to your overly complicated website. Create a simple LP focused only on getting conversions. Match ad tone, visuals and messaging. Reduce barriers and distractions.

 

7. Allocate a Budget, Set Up Tracking and Launch Ads

 

Start small to test performance across platforms, placements and creatives. Optimize over time, scaling winners. Install tracking pixels, UTM tags to attribute results.

 

8. Continuously Track Results and Optimize

 

Look beyond vanity metrics at ROI. Kill losers quickly, scale winners aggressively. Focus on CAC, ROAS, LTV at campaign and adset level. Try to improve CTR and conversions.

 

9. Relentlessly Test and Iterate

 

Regularly test new targeting, creatives, offers, placements. Take top performers and build upon them. Be disciplined in analyzing data to guide optimizations.

...

You are an expert consultant and politely ask the user specific questions about their ad requirements based on the above process.  Along the way you advise the user, and where possible will create the required items for the user  Reason step by step.."""

    chat_prompt = [{"role": "system", "content": user_prompt}, {"role": "assistant", "content": 'Use the chat memory to help the user build an ad.'}] + memory

    response = openai.ChatCompletion.create(model="gpt-4", messages=chat_prompt)
    bot_message = response["choices"][0]["message"]["content"]

    bot_memory = ChatMemory(user_id=current_user.id, role="assistant", content=bot_message)
    db.session.add(bot_memory)
    db.session.commit()

    return jsonify({'bot_message': bot_message})
