import json

visited = {}
with open("Data.json") as jfile:
    temp = json.load(jfile)
    for entry in temp:
        if entry['url'] in visited:
            visited[entry['url']] += 1
            continue
        visited[entry['url']] = 1
            
for url, count in visited.items():
    if count > 1:
        print(f"URL: {url}\nCount .......... {count}")