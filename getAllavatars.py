from pathlib import Path

def read_text_file():
    file_path = Path.cwd() / "x.txt"
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return {}

    data = {line.split(' : ')[0].strip(): line.split(' : ')[1].strip() for line in lines if ' : ' in line}
    return data


