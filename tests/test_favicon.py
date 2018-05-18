import pytest
from bs4 import BeautifulSoup

import favicon
from favicon.favicon import dimensions, is_absolute

s = BeautifulSoup('')


def test_default(m):
    m.get('http://mock.com/', text='body')
    m.head('http://mock.com/favicon.ico', text='icon')
    m.get('http://mock.com/favicon.ico', text='icon')

    icons = favicon.get('http://mock.com/')
    assert icons

    icon = icons[0]
    assert icon.url == 'http://mock.com/favicon.ico'
    assert icon.format == 'ico'


@pytest.mark.parametrize('link', [
    '<link rel="icon" href="favicon.ico">',
    '<link rel="ICON" href="favicon.ico">',
    '<link rel="shortcut icon" href="favicon.ico">',
    '<link rel="apple-touch-icon" href="favicon.ico">',
    '<link rel="apple-touch-icon-precomposed" href="favicon.ico">',
], ids=[
    'icon',
    'ICON',
    'shortcut icon',
    'apple-touch-icon',
    'apple-touch-icon-precomposed',
])
def test_link_rel_attribute(m, link):
    m.head('http://mock.com/favicon.ico', text='Not Found', status_code=404)
    m.get('http://mock.com/', text=link)

    icons = favicon.get('http://mock.com/')
    assert icons

    icon = icons[0]
    assert icon.url == 'http://mock.com/favicon.ico'
    assert icon.width == 0 and icon.height == 0
    assert icon.format == 'ico'


def test_link_sizes_attribute(m):
    m.head('http://mock.com/favicon.ico', text='Not Found', status_code=404)
    m.get('http://mock.com/',
          text='<link rel="icon" '
               'sizes="16x16 32x32" '
               'type="image/png"'
               'href="http://mock.com/favicon.png">')

    icons = favicon.get('http://mock.com/')
    assert icons

    icon = icons[0]
    assert icon.url == 'http://mock.com/favicon.png'
    assert icon.width == 32 and icon.height == 32
    assert icon.format == 'png'


def test_link_apple_touch(m):
    m.head('http://mock.com/favicon.ico', text='Not Found', status_code=404)
    m.get('http://mock.com/',
          text='<link rel="apple-touch-icon" '
               'href="/static/apple-touch-icon-144x144.png">')

    icons = favicon.get('http://mock.com/')
    assert icons

    icon = icons[0]
    assert icon.url == 'http://mock.com/static/apple-touch-icon-144x144.png'
    assert icon.width == 144 and icon.height == 144
    assert icon.format == 'png'


@pytest.mark.parametrize('url,expected', [
    ('http://mock.com/favicon.ico', True),
    ('favicon.ico', False),
    ('/favicon.ico', False),
])
def test_is_absolute(url, expected):
    assert is_absolute(url) == expected


@pytest.mark.parametrize('link,size', [
    (s.new_tag('link', href='logo.png', sizes='any'), (0, 0)),
    (s.new_tag('link', href='logo.png', sizes='16x16'), (16, 16)),
    (s.new_tag('link', href='logo.png', sizes='16x16+'), (16, 16)),
    (s.new_tag('link', href='logo.png', sizes='16x16 32x32'), (32, 32)),
    (s.new_tag('link', href='logo.png', sizes='32x32 16x16'), (32, 32)),
    (s.new_tag('link', href='logo-64x64.png', sizes='any'), (64, 64)),
], ids=lambda l: str(l['sizes']) if not isinstance(l, tuple) else None)
def test_dimensions(link, size):
    assert dimensions(link) == size
