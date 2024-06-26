import keys
import threading
import queue
import random

import openai
import google.generativeai as genai
import anthropic

openai.api_key = keys.openai_token
genai.configure(api_key=keys.gemini_token)
anthropic_client = anthropic.Client(api_key=keys.anthropic_token)

def gemini_query(prompt, model='gemini-1.5-flash', max_tokens=100, pure_text=True):
    print(f'{model} checking in')
    _model = genai.GenerativeModel(model)
    temperature = random.uniform(0.05, 0.95)
    generation_config = genai.GenerationConfig(
    temperature=temperature,
    max_output_tokens=max_tokens,
    )
    response = _model.generate_content(prompt, generation_config=generation_config)
    if pure_text:
        return response.text.strip()
    else:
        yes_no = response.text.strip().split(':')[0]
        motivation = response.text.strip().split(':')[1]
        return {'model':model, 'vote':yes_no, 'motivation':motivation}


def gpt3_query(prompt, model='gpt-3.5-turbo-instruct', max_tokens=100, pure_text=True) -> None:
    print(f'{model} checking in')
    temperature = random.uniform(0.05, 0.95)
    response = openai.completions.create(model=model, prompt=prompt, max_tokens=max_tokens, temperature=temperature)
    if pure_text:
        return response.choices[0].text.strip()
    else:
        yes_no = response.choices[0].text.strip().split(':')[0]
        motivation = response.choices[0].text.strip().split(':')[1]
        return {'model':model, 'vote':yes_no, 'motivation':motivation}


def gpt4_query(prompt, model='gpt-4o', max_tokens=100, pure_text=True) -> None:
    print(f'{model} checking in')
    temperature = random.uniform(0.05, 0.95)
    response = openai.chat.completions.create(model=model, messages=[{"role":"user", "content":prompt}], max_tokens=max_tokens, temperature=temperature)
    if pure_text:
        return response.choices[0].message.content
    else:
        yes_no = response.choices[0].message.content.split(':')[0]
        motivation = response.choices[0].message.content.split(':')[1]
        return {'model':model, 'vote':yes_no, 'motivation':motivation}


def anthropic_query(prompt, model='claude-2.1', max_tokens=100, pure_text=True):
    print(f'{model} checking in')
    temperature = random.uniform(0.05, 0.95)
    response = anthropic_client.messages.create(model=model, messages=[{"role":"user", "content":prompt}], max_tokens=max_tokens, temperature=temperature)
    if pure_text:
        return response.content[0].text.strip()
    else:
        yes_no = response.content[0].text.strip().split(':')[0]
        motivation = response.content[0].text.strip().split(':')[1]
        return {'model':model, 'vote':yes_no, 'motivation':motivation}


def send_query(prompt, results_queue, max_tokens=100, random_run=True) -> None:
    print('',flush=True)
    all_models = [ 
        {
            'engine' : gemini_query,
            'model' : 'gemini-1.5-flash'
        },
        {
            'engine' : gemini_query,
            'model' : 'gemini-1.5-pro'
        },
        {
            'engine' : gpt3_query,
            'model' : 'gpt-3.5-turbo-instruct',
        },
        {
            'engine' : gpt4_query,
            'model' : 'gpt-3.5-turbo-0125',
        },
        {
            'engine' : gpt4_query,
            'model' : 'gpt-4-0613'
        },
        {
            'engine' : gpt4_query,
            'model' : 'gpt-4-turbo-2024-04-09'
        },
        {
            'engine' : gpt4_query,
            'model' : 'gpt-4o'
        },
        {
            'engine' : anthropic_query,
            'model' : 'claude-2.1'
        },
        {
            'engine' : anthropic_query,
            'model' : 'claude-3-haiku-20240307'
        },    
    ]

    if random_run:
        select_function = random.choice(all_models)
    else:
        if not hasattr(send_query, "list_tracker"):
            send_query.list_tracker = -1
            send_query.lock = threading.Lock()

        with send_query.lock:
            if send_query.list_tracker == len(all_models) - 1:  # Adjust the check to account for index bounds
                send_query.list_tracker = 0
            else:
                send_query.list_tracker += 1

            print(send_query.list_tracker)
            select_function = all_models[send_query.list_tracker]
    response = select_function['engine'](prompt, model=select_function['model'], pure_text=False)
    results_queue.put(response)


def validate_query(text_to_validate, number_of_voters=3) -> list:
    validation_query = f"Is the following statement true? Answer with only 'Yes' or 'No', a colon(:) and a one sentence explaination of the result.: {text_to_validate}"

    results_queue = queue.Queue()
    threads = []
    for voter in range(number_of_voters):
        thread = threading.Thread(target=send_query, args=(validation_query, results_queue, 100, True, ))
        threads.append(thread)
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(timeout=5)

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    return results


# Set the params
limit_for_true = 0.5
quorum_voters = 3
# Ask the main question
prompt = "Answer this in a complete sentence: What company creates the most cars in the world?"
print(prompt)
print('---')
# prompt = "Answer this in a complete sentence: What is the biggest company in the world?"
result = gpt3_query(prompt)


# Let's see the votes
quorum_result = validate_query(result,quorum_voters)
# print(quorum_result)

# Calculate the outcome
from collections import Counter
counts = Counter(f"{qr['model']},{qr['vote']}" for qr in quorum_result)
for key, value in counts.items():
    print(f'{key}:{value}')

print('---')

yes_votes = sum(d['vote'] == 'Yes' for d in quorum_result)
percentage_yes = (yes_votes / len(quorum_result)) 
print ('True' if percentage_yes > limit_for_true else "False") 

print('---')

for q in quorum_result:
    print(f"{q['model']} - {q['vote']} - {q['motivation']}")