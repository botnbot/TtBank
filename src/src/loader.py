import json

def load_user_settings(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# def load_data_from_file(path_to_datafile: str) -> list[dict]:
#     transactions = convert_xlsx_to_list(path_to_datafile)
#     return transactions
