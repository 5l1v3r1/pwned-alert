from nose.tools import assert_equal, make_decorator

import scan


def func(test_case):
    'Provide a shortcut for the corresponding function.'
    f = getattr(scan, test_case.__name__.replace('test_', ''))
    return make_decorator(test_case)(lambda: test_case(f))


@func
def test_find_php_constants(f):
    code = '''
        // define ('DB_PASSWORD','');
        define( 'DB_HOST', 'localhost' );
        #define DB_PASSWORD "test"
        define("DB_NAME",'admin');
        defined('DB_USERNAME') or define('DB_USERNAME', 'vagrant');
    '''
    expect = [
        ('DB_PASSWORD', ''),
        ('DB_HOST', 'localhost'),
        ('DB_NAME', 'admin'),
        ('DB_USERNAME', 'vagrant'),
    ]
    assert_equal(list(f(code)), expect)