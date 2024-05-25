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

def gemini_query(prompt, model='gemini-1.5-flash', max_tokens=100):
    print('Gemini checking in')
    _model = genai.GenerativeModel(model)
    temperature = random.uniform(0.05, 0.95)
    generation_config = genai.GenerationConfig(
    temperature=temperature,
    max_output_tokens=max_tokens,
    )
    response = _model.generate_content(prompt, generation_config=generation_config)
    return {'model':model, 'vote':response.text.strip()}

def openai_query(prompt, model='gpt-3.5-turbo-instruct', max_tokens=100) -> None:
    print('OpenAI checking in')
    temperature = random.uniform(0.05, 0.95)
    response = openai.completions.create(model=model, prompt=prompt, max_tokens=max_tokens, temperature=temperature)
    return {'model':model, 'vote':response.choices[0].text.strip()}

def anthropic_query(prompt, model='claude-2.1', max_tokens=100):
    print('Anthropic checking in')
    temperature = random.uniform(0.05, 0.95)
    response = anthropic_client.messages.create(model=model, messages=[{"role":"user", "content":prompt}], max_tokens=max_tokens, temperature=temperature)
    return {'model':model, 'vote':response.content[0].text.strip()}

def send_query(prompt, results_queue, max_tokens=100) -> None:
    print('',flush=True)
    functions = [gemini_query, openai_query, anthropic_query]
    random_function = random.choice(functions)
    response = random_function(prompt)
    results_queue.put(response)

def validate_query(text_to_validate, number_of_voters=3) -> list:
    validation_query = f"Is the following statement true? Answer with only 'Yes' or 'No': {text_to_validate}"

    results_queue = queue.Queue()
    threads = []
    for voter in range(number_of_voters):
        thread = threading.Thread(target=send_query, args=(validation_query, results_queue,))
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
# prompt = "Answer this in a complete sentence: What company creates the most cars in the world?"
prompt = "Answer this in a complete sentence: What is the biggest company in the world?"
result = openai_query(prompt)
# result = gemini_query(prompt)
# result = anthropic_query(prompt)
print(result)

# Let's see the votes
quorum_result = validate_query(result,quorum_voters)
# print(quorum_result)

# Calculate the outcome
from collections import Counter
counts = Counter(f"{qr['model']},{qr['vote']}" for qr in quorum_result)
for key, value in counts.items():
    print(f'{key}:{value}')

yes_votes = sum(d['vote'] == 'Yes' for d in quorum_result)
percentage_yes = (yes_votes / len(quorum_result)) 
print ('True' if percentage_yes > limit_for_true else "False") 