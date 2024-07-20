from typing import Callable

def input_validated[T](prompt: str, convert: Callable[[str], T], validate: Callable[[T], bool], errorMessage: str) -> T | None:
    '''Запрашивает у пользователя ввод, пока пользователь не введёт значение,
    успешно преобразуемое функцией convert и валидируемое функцией validate
    Возвращает результат преобразования (вызова convert) или None, если было поднято исключение KeyboardInterrupt

    Аргументы:
    prompt : str -- Отображаемое при запросе ввода сообщение
    convert : Callable[[str], T] -- функция-конвертер для преобразования входной строки к желаемому типу. Может поднимать исключение ValueError.
    validate : Callable[[T], bool] -- функция-валидатор для валидации преобразованного значения. Должна возвращать True, если значение валидно, False иначе.
    errorMessage : str -- сообщение, которое будет выведено, если будет поднято исключение ValueError или validate вернёт False.
    '''
    while True:
        try:
            user_input = input(prompt)
            result : T = convert(user_input)
            if not validate(result):
                raise ValueError
            return result
        except ValueError:
            print(errorMessage)
        except KeyboardInterrupt:
            return None

def converter_string(x : str) -> str:
    '''Функция-конвертер для input_validated, убирающая whitespace-символы из начала и конца строки'''
    return x.strip()

def converter_int(x: str) -> int:
    '''Функция-конвертер для input_validated, парсящая строку как целое число'''
    return int(x)

def validator_string_not_empty(x : str) -> bool:
    '''Функция-валидатор для input_validated, проверяющая, не пустая ли строка'''
    return len(x) > 0

def validator_always(_ : object) -> bool:
    '''Функция-валидатор для input_validate, принимающая любое значение как валидное'''
    return True