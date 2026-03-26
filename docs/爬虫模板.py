# 爬虫模板

import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f'Error fetching {url}: {e}')
        return None


def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

if __name__ == '__main__':
    url = 'http://example.com'
    page = fetch_page(url)
    if page:
        soup = parse_html(page.text)
        # 在这里添加解析逻辑
