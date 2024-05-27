all_models = [ 
    {
        'engine' : 'gemini_query',
        'model' : 'gemini-1.5-flash'
    },
    {
        'engine' : 'openai_query',
        'model' : 'gpt-3.5-turbo-instruct',
    },
    {
        'engine' : 'openai_query',
        'model' : 'gpt-3.5-turbo-0125',
    },
    {
        'engine' : 'openai_query',
        'model' : 'gpt-4-0613'
    },
    {
        'engine' : 'openai_query',
        'model' : 'gpt-4-turbo-2024-04-09'
    },
    {
        'engine' : 'openai_query',
        'model' : 'gpt-4o'
    },
    {
        'engine' : 'anthropic_query',
        'model' : 'claude-2.1'
    },
]
print(len(all_models))