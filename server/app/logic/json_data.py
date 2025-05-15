import json


def write(path, objects_list):
    methods_dict_list = []
    for i in objects_list:
        methods_dict_list.append(i.__dict__)
    write_dict_list(path, methods_dict_list)


def write_dict_list(path, list_dict):
    with open(path, "w") as f:
        json_txt = json.dumps(list_dict, indent=2, default=str)
        f.write(json_txt)


def read(path):
    with open(path, "r") as f:
        content = f.read()
    return json.loads(content)
