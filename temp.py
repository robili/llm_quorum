a = [{'model': 'gpt-3.5-turbo-instruct', 'vote': 'No'}, {'model': 'claude-2.1', 'vote': 'Yes'}, {'model': 'claude-2.1', 'vote': 'Yes'}, {'model': 'claude-2.1', 'vote': 'No'}]

from collections import Counter
counts = Counter(f"{d['model']},{d['vote']}" for d in a)
for key, value in counts.items():
    print(f'{key}:{value}')



yes_votes = sum(d['vote'] == 'Yes' for d in a)
print(yes_votes)
print(len(a))
exit()


vote_counts = Counter(qr['vote'] for qr in a)
for vote, count in vote_counts.items():
    print(f"{vote}: {count}")