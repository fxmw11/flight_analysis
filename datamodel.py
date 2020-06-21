import json


class DictItem:
    def __init__(self, values={}, cnt=1):
        self.count = cnt
        self.values = values

    def __add__(self, values):
        self.count += 1
        for k, v in values.items():
            if k in self.values.keys():
                self.values[k] += v
            else:
                self.values[k] = v
        return self

    def to_json(self):
        v = self.values.copy()
        v['count'] = self.count
        return v

    def __repr__(self):
        v = self.values.copy()
        v['count'] = self.count
        return str(v)

    def __str__(self):
        return str(self.__repr__())


class Dict2Level:
    def __init__(self):
        self.dict = {}

    def sort_keys(self, a, b):
        if type(a) != str or type(b) != str:
            return [None, None]
        return sorted([a, b])

    def add(self, a, b, values={}, cnt=1):
        a, b = self.sort_keys(a, b)
        if a is not None:
            if a in self.dict.keys():
                if b in self.dict[a].keys():
                    self.dict[a][b] += values
                    self.dict[a][b].count += cnt - 1
                else:
                    self.dict[a][b] = DictItem(values, cnt)
            else:
                self.dict[a] = {b: DictItem(values, cnt)}

    def get_dict(self):
        return self.dict


def dict2json(dict, file_name, var_name):
    data = json.dumps(dict, sort_keys=True, indent=4, default=json_dump)
    data = f"var {var_name} = `{data}`" # drop json in a js-variable for easier local testing
    with open(file_name, "w") as file:
        file.write(data)


def json_dump(obj):
    try:
        return obj.to_json()
    except:
        return obj.__dict__