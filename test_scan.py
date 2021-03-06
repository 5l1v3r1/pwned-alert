import random
from unittest import mock

import scan


def func(test_case):
    'Provide a shortcut for the corresponding function.'
    f = getattr(scan, test_case.__name__.replace('test_', ''))
    return lambda: test_case(f)


@func
@mock.patch('scan.requests.get')
def test_search_code(f, http_mock):
    PAGES, ITEMS = 5, 30

    values = [
        {'items': [random.random() for i in range(ITEMS)]}
        for j in range(PAGES)
    ]
    values.append({'items': []})
    http_mock.return_value = mock.Mock(json=mock.Mock(side_effect=values))

    expect = sum((d['items'] for d in values), [])
    assert list(f('', pause=0)) == expect
    assert http_mock.call_count == PAGES + 1


@func
def test_find_php_constants(f):
    code = '''
        // define ('DB_PASSWORD','');
        define( 'DB_HOST', 'localhost' );
        #define DB_PASSWORD "test"
        define("DB_NAME",'admin');
        defined('DB_USERNAME') or define('DB_USERNAME', 'vagrant');
        define("PAGE_SIZE", 5);
    '''
    expect = [
        ('DB_PASSWORD', ''),
        ('DB_HOST', 'localhost'),
        ('DB_NAME', 'admin'),
        ('DB_USERNAME', 'vagrant'),
    ]
    assert list(f(code)) == expect


@func
@mock.patch('scan.find_php_constants')
def test_find_php_db_password(f, constants_mock):
    constants_mock.return_value = [
        ('PASSWORD', ''),
        ('PASSWORD', 'root'),
        ('HOSTNAME', 'localhost'),
        ('PASSWORD', 'localhost-8080.com'),
        ('PASSWORD', '{% pass %}'),
        ('PASSWORD', '1234567'),
        ('PASSWORD', '*******'),
        ('PASSWORD', 'correct'),
    ]
    assert f('') == 'correct'
