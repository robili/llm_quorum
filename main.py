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
    model = genai.GenerativeModel(model)
    response = model.generate_content(prompt)
    return response.text.strip()

def openai_query(prompt, model='gpt-3.5-turbo-instruct', max_tokens=100) -> None:
    print('OpenAI checking in')
    response = openai.completions.create(model=model, prompt=prompt, max_tokens=max_tokens)
    return response.choices[0].text.strip()

def anthropic_query(prompt, model='claude-2.1', max_tokens=100):
    print('Anthropic checking in')
    response = anthropic_client.messages.create(model=model, messages=[{"role":"user", "content":prompt}], max_tokens=max_tokens)
    return response.content[0].text.strip()

def send_query(prompt, results_queue, max_tokens=100) -> None:
    print(prompt)
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

truth_limit = 0.5
quorum_voters = 5

prompt = "Answer this in a complete sentence: What company creates the most cars in the world?"
result = openai_query(prompt)
# result = gemini_query(prompt)
# result = anthropic_query(prompt)
print(result)

quorum_result = validate_query(result,quorum_voters)
print(quorum_result)

yes_votes = quorum_result.count('Yes')
percentage_yes = (yes_votes / len(quorum_result)) 
print ('True' if percentage_yes > 0.5 else "False") 