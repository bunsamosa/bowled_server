import json
import random

with open("first_names.txt", encoding="UTF-8") as f:
    x = f.readlines()
    first_names = [i.strip() for i in x]

with open("last_names.txt", encoding="UTF-8") as f:
    x = f.readlines()
    last_names = [i.strip() for i in x]

final_names = set()
for _ in range(10000):
    fn = random.choice(first_names)
    ln = random.choice(last_names)

    final_names.add(f"{fn} {ln}")

with open("final_names.json", "w", encoding="UTF-8") as f:
    json.dump(tuple(final_names), f)
