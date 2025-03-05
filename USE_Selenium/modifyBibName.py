import json
import re



def modifyBibName(conference):
    keyfile = {}

    def getKey(url):
        pattern =  r'/([A-Za-z0-9]+)\.html'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None


    with open(f"{conference}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for key, value in data.items():
            n = getKey(value)
            if n:
                keyfile[n] = key.replace("?", "").replace(":", "").replace("：","").replace(".", "").replace("\"", "")

    import os

    for filename in os.listdir("C:\\Users\\mengsi\\Downloads"):
        if filename.endswith(".bib"):
            print(filename)
            if filename.split(".bib")[0] in keyfile:
                os.rename(f"C:\\Users\\mengsi\\Downloads\\{filename}", f"C:\\Users\\mengsi\\Downloads\\{keyfile[filename.split('.bib')[0]]}.bib")


if __name__ == "__main__":
    modifyBibName("iclr2024['llm']")