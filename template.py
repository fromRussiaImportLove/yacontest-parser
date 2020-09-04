"""
<DESCRIPTION>
"""

import logging

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

FIXTURES = [
    """
    #input_n
    #input_data
    """, """
    #output_data
    """,
]


def take_data(fixtures):
    """Забираем данные с инпута для контеста, или из фикстур для тестов"""
    if fixtures is None:
        fixtures = [input(), input()]

    n = fixtures.pop(0)
    array = list(map(str, fixtures.pop(0).split()))
    return n, array


def solve(fixtures=None):
    """Здесь пишем логику решения"""
    n, data = take_data(fixtures)
    return data[0].replace('in', 'out')


def testing():
    """
    Фикстуры идут по порядку: группа с входными данными, группа с ответом.
    Несколько стрипов позволяют не париться насчет табуляции в фикстурах.
    """

    tests = []
    for n, f in enumerate(FIXTURES, 1):
        # забираем входные данные
        if n % 2 == 1:
            tests.append([list(map(str.lstrip, f.strip().split('\n')))])
        # забираем ответ
        else:
            tests[(n - 1) // 2].append(list(map(str.lstrip, f.strip().split('\n'))))

    for test in tests:
        # test[0] - input data, test[1] - список ожидаемого ответа
        result = solve(test[0].copy())
        # ответ может быть набором строк: нужно корректировать что забирать из test[1]
        answer = test[1][0]
        print(f'{test} {answer} {result}')
        if result != answer:
            logger.setLevel(logging.INFO)
            result = solve(test[0].copy())
            assert result == answer, (test[0], test[1], result)


def run(test_mode=False):
    """При запуске из папки PyCharm или флаге test_mode тестируем FIXTURES"""
    if 'pycharm-professional' in __loader__.path or test_mode:
        return testing()

    # Иногда контест ждет несколько строк вывода,тогда принт здесь не поможет
    print(solve())


if __name__ == '__main__':
    run()
