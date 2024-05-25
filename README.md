# LLM quorum 

A simple script that asks llm:s to validate a result of an llm query. A number of llm:s (Gemini, GPT, Anthropic) are asked to vote on a statement and return Y or N. The votes are counted and based on the minimum threshold, it'll return True or False.

The idea is that this will lower the risk of an answer being wrong, at the cost of extra processing. Useful if a bad answer can be costly (like with a customer support chatbot.)

Note that this is just a very basic test. A real world scenario there needs to be more work to be done. For instance a bit of pre-processing, and pulling out of statements to validate (if it's a long answer). 
