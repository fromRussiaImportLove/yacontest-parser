import requests
import os
from bs4 import BeautifulSoup
from secret import cookie

# Номера уже пройденных контестов: 18337, 18338, 18357, 18358, 18359, 18360,

CONTEST = '18360'
URL = f'https://contest.yandex.ru/contest/{CONTEST}/problems/'
HOST = 'https://contest.yandex.ru'
TEMPLATE = 'template.py'

FIXTURE_SIGNATURE = """\"\"\"
    #input_n
    #input_data
    \"\"\", \"\"\"
    #output_data
    \"\"\","""

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
    'accept': '*/*',
    'Cookie': cookie,
}


def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return r


def get_problems_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    problems_block = soup.find('ul',
                               class_='tabs-menu tabs-menu_theme_normal tabs-menu_layout_vert tabs-menu_size_m tabs-menu_role_problems inline-block i-bem')
    if problems_block is None:
        return None, []
    problems_tabs = problems_block.find_all('li', class_="tabs-menu__tab")
    problems_link = []

    for tab in problems_tabs:
        problems_link.append(
            HOST + tab.find('a', class_='link').get('href'),
        )

    contest_name = soup.find('div', class_='contest-head__item contest-head__item_role_title').get_text().split(':')[1]

    return contest_name, problems_link


def get_problem_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    problem = soup.find('div', class_='problem-statement')

    fixtures = soup.find_all('table', class_='sample-tests')
    problem_title = problem.find_next('h1', class_='title').get_text()
    problem_descr = (
        problem_title.strip() +
        '\n' + problem.find('div', class_='legend').get_text().strip() +
        '\n\nФорма ВВОДА\n' + problem.find('div', class_='input-specification').get_text().strip() +
        '\n\nФорма ВыВОДА\n' + problem.find('div', class_='output-specification').get_text().strip()
    )

    problem_fixtures = {}

    for fixture in fixtures:
        problem_fixtures[fixture.find('td').get_text()] = fixture.find_next('td').get_text()

    return problem_title, problem_descr, problem_fixtures


def convert_fix_dict_to_signature_format(fixtures):
    data = ''
    for input, output in fixtures.items():
        data += '\"\"\"\n'
        data += input
        data += '\"\"\", \"\"\"\n'
        data += output
        data += '\"\"\",\n'
    return data


def make_problem_file(dirname, filename, problem, fixtures, link):
    if not os.path.exists(path := f'{dirname}/{filename}.py'):
        with open(TEMPLATE, 'r') as f:
            template_data = f.read()
        problem = link + '\n' + problem
        template_data = template_data.replace('<DESCRIPTION>', problem)
        template_data = template_data.replace(FIXTURE_SIGNATURE, convert_fix_dict_to_signature_format(fixtures))

        with open(path, 'tw', encoding='utf-8') as f:
            f.write(template_data)

        print(f'File {filename}.py has been created.')

    else:
        print(f'File {filename}.py EXIST! Not append data.')


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        contest_name, problem_links = get_problems_links(html.text)
        if contest_name and problem_links:
            contest_dir = CONTEST + contest_name
            if not contest_dir[-1].isalnum():
                contest_dir = contest_dir[:-1]
            if not os.path.exists(contest_dir):
                os.mkdir(contest_dir)
                print(f'Created {contest_dir=}')

        else:
            print(f'Check you contest. Maybe you are not start yet.')

        for link in problem_links:
            html = get_html(link)
            if html.status_code == 200:
                filename, problem_data, fixtures = get_problem_data(html.text)
                make_problem_file(contest_dir, filename, problem_data, fixtures, link)
        print(f'# Work complete. Check folders')

    else:
        print('Error. Cant get page. Check URL and cookie')


if __name__ == '__main__':
    parse()
