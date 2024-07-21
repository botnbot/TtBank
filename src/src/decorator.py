import json
import functools

def write_result_to_json(file_path):
    def decorator_write_result(func):
        @functools.wraps(func)
        def wrapper_write_result(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=4)
            return result
        return wrapper_write_result
    return decorator_write_result

# Пример использования
@write_result_to_json('result.json')
def compute_sum(a, b):
    return {'sum': a + b}

# Вызов функции
result = compute_sum(3, 5)
print(result)  # Это должно вывести {'sum': 8}, а результат будет записан в файл 'result.json'
