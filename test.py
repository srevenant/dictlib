import doctest
import dictlib
from pylint import epylint as lint

doctest.testmod(dictlib)

lint.py_run('dictlib')
