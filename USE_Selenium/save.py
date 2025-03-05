import json
import os

class Save(object):
    def __init__(self, data, filename):
        self.data = data
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self._save(filename if filename.endswith(".json") else filename+".json")

    def _save(self, filename):
        file_dir = os.path.join(self.dir, filename)
        with open(f"{file_dir}", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        print("数据已保存到{}".format(filename))