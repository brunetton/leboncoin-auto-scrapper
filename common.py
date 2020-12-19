import json

def ensure_list(value):
    return value if isinstance(value, (list, tuple)) else [value]


def write_json_file(file_path, data):
    with file_path.open('w', encoding='utf-8') as file_:
        json.dump(data, file_, ensure_ascii=False)
