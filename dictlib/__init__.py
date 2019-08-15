"""
Dictionary Utility Library

Copyright 2016 Brandon Gillespie

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import copy
import re

__version__ = 1.0

################################################################################
RX_INDEX = re.compile(r'(.*)\[(\d+)\]$')

def _splice_index(*key):
    """
    Utility for key management in dig/dug

    If first elem of key list contains an index[], spread it out as a second
    numeric index.

    >>> _splice_index('abc[0]', 'def')
    ('abc', 0, 'def')
    >>> _splice_index('abc[a]', 'def')
    ('abc[a]', 'def')
    >>> _splice_index('abc[200]', 'def')
    ('abc', 200, 'def')
    >>> _splice_index('abc', 'def')
    ('abc', 'def')
    >>> _splice_index(0, 'abc', 'def')
    (0, 'abc', 'def')
    """
    if isinstance(key[0], str):
        result = RX_INDEX.search(key[0])
        if result:
            return tuple([result.group(1), int(result.group(2))] + list(key[1:]))
    return key

def dig(obj, key):
    """
    Recursively pull from a dictionary, using dot notation.  See also: dig_get
    >>> dig({"a":{"b":{"c":1}}}, "a.b.c")
    1
    """
    array = key.split(".")
    return _dig(obj, *array)

def _dig(obj, *key):
    """
    Recursively lookup an item in a nested dictionary,
    using an array of indexes

    >>> _dig({"a":{"b":{"c":1}}}, "a", "b", "c")
    1
    """
    key = _splice_index(*key)

    if len(key) == 1:
        return obj[key[0]]
    return _dig(obj[key[0]], *key[1:])

################################################################################
def dig_get(obj, key, *default):
    """
    Recursively pull from a dictionary, using dot notation, with default value
    instead of raised error (similar to dict.get()).

    >>> dig_get({"a":{"b":{"c":1}}}, "a.b.d")
    >>> dig_get({"a":{"b":{"c":1}}}, "a.b.d", 2)
    2
    >>> dig_get({"a":{"b":[{"c":1},{"d":4}]}}, "a.b[1].d", 2)
    4
    """
    array = key.split(".")
    if default:
        default = default[0]
    else:
        default = None
    try:
        return _dig_get(obj, default, *array)
    except (KeyError, AttributeError):
        return default

def _dig_get_elem(obj, key, default):
    try:
        return obj[key]
    except (IndexError, KeyError):
        return default

def _dig_get(obj, default, *key):
    """
    Recursively lookup an item in a nested dictionary,
    using an array of indexes, with a default value

    >>> _dig_get({"a":{"b":{"c":1}}}, 2, "a", "b", "d")
    2
    >>> _dig_get({"a":{"b":{"c":1}}}, 2, "a", "b", "c")
    1
    >>> _dig_get({"a":{"b":{"c":1}}}, 0, "a", "z", "c")
    0
    """
    key = _splice_index(*key)
    if not obj:
        return default
    if len(key) == 1:
        return _dig_get_elem(obj, key[0], default)
    return _dig_get(_dig_get_elem(obj, key[0], default), default, *key[1:])

def dug(obj, key, value):
    """
    Inverse of dig: recursively set a value in a dictionary, using
    dot notation.

    >>> test = {"a":{"b":{"c":1}}}
    >>> dug(test, "a.b.c", 10)
    True
    >>> test
    {'a': {'b': {'c': 10}}}
    """
    array = key.split(".")
    return _dug(obj, value, *array)

def _dug(obj, value, *key):
    key = _splice_index(*key)

    # pylint: disable=no-else-return
    if len(key) == 1:
        obj[key[0]] = value
        return True
    elif not key[0] in obj:
        obj[key[0]] = {}
    return _dug(obj[key[0]], value, *key[1:])

################################################################################
def union(dict1, dict2):
    """
    Deep merge of dict2 into dict1.  May be dictionaries or dictobj's.
    Values in dict2 will replace values in dict1 where they vary but have
    the same key.

    When lists are encountered, the dict2 list will replace the dict1 list.

    This will alter the first dictionary.  The returned result is dict1, but
    it will have references to both dictionaries.  If you do not want this,
    use union_copy(), which is less efficient but data-safe.

    >>> a = dict(a=dict(b=dict(c=1)))
    >>> b = dict(a=dict(b=dict(d=2)),e=[1,2])
    >>> # sorted json so that it is predictably the same
    >>> import json
    >>> json.dumps(union(a, b), sort_keys=True)
    '{"a": {"b": {"c": 1, "d": 2}}, "e": [1, 2]}'
    >>> json.dumps(a, sort_keys=True)
    '{"a": {"b": {"c": 1, "d": 2}}, "e": [1, 2]}'
    >>> json.dumps(b, sort_keys=True)
    '{"a": {"b": {"d": 2}}, "e": [1, 2]}'
    >>> a['e'][0] = 3
    >>> json.dumps(a, sort_keys=True)
    '{"a": {"b": {"c": 1, "d": 2}}, "e": [3, 2]}'
    >>> json.dumps(b, sort_keys=True)
    '{"a": {"b": {"d": 2}}, "e": [3, 2]}'
    """
    for key, value in dict2.items():
        if key in dict1 and isinstance(value, dict):
            dict1[key] = union(dict1[key], value)
        else:
            dict1[key] = value
    return dict1

################################################################################
# pylint: disable=too-many-branches
def union_setadd(dict1, dict2):
    """
    Similar to dictlib.union(), but following a setadd logic (with strings and ints),
    and a union (with dictionaries).  Assumption is that all elements of the list
    are of the same type (i.e. if first element is a dict, it tries to union all
    elements)

    NOT data safe, it mangles both dict1 and dict2

    >>> a = dict(a=[{"b":1, "c":2},{"a":1}], b=dict(z=dict(y=1)), e=[1])
    >>> b = dict(a=[{"b":1, "d":3}], b=dict(z=dict(y=-1)), e=[1,2])
    >>> # sorted json so that it is predictably the same
    >>> import json
    >>> json.dumps(union_setadd(a, b), sort_keys=True)
    '{"a": [{"b": 1, "c": 2, "d": 3}, {"a": 1}], "b": {"z": {"y": -1}}, "e": [1, 2]}'
    >>> a['a'][0]["d"] = 4
    >>> json.dumps(b, sort_keys=True)
    '{"a": [{"b": 1, "d": 3}], "b": {"z": {"y": -1}}, "e": [1, 2]}'
    >>> json.dumps(a, sort_keys=True)
    '{"a": [{"b": 1, "c": 2, "d": 4}, {"a": 1}], "b": {"z": {"y": -1}}, "e": [1, 2]}'
    """
    for key2, val2 in dict2.items(): # pylint: disable=too-many-nested-blocks
        # if key is in both places, do a union
        if key2 in dict1:
            # if dict2 val2 is a dict, assume dict1 val2 is as well
            if isinstance(val2, dict):
                dict1[key2] = union_setadd(dict1[key2], val2)
            # if dict2 val2 is a list, things get uglier
            elif isinstance(val2, list):
                val1 = dict1[key2]
                # both dict1/dict2 need to be lists
                if not isinstance(val1, list):
                    raise TypeError("dict1[{key}] is not a list where dict2[{key}] is."
                                    .format(key=key2))
                # ignore zero length val2 (string or list)
                if not val2:
                    continue
                # if val2's first element is a dict, assume they are all dicts
                if isinstance(val2[0], dict):
                    for xelem in range(0, len(val2)): # pylint: disable=consider-using-enumerate
                        if xelem < len(val1):
                            val1[xelem] = union_setadd(val1[xelem], val2[xelem])
                        else:
                            val1.append(val2[xelem])
                # otherwise just setadd the elements by value; order can get wonky
                else:
                    for elem in val2:
                        if elem not in val1: # inefficient
                            val1.append(elem)
                dict1[key2] = val1
            # any other type: just assign
            else:
                dict1[key2] = val2
        # or just define it
        else:
            dict1[key2] = val2
    return dict1

################################################################################
def union_copy(dict1, dict2):
    """
    Deep merge of dict2 into dict1.  May be dictionaries or dictobj's.
    Values in dict2 will replace values in dict1 where they vary but have
    the same key.

    Result is a new dictionary.  Less efficient than union()

    If there are multiple pointers to same value, this will make multiple copies.

    >>> a = dict(a=dict(b=dict(c=1)))
    >>> b = dict(a=dict(b=dict(d=2)),e=[1,2])
    >>> # sorted json so that it is predictably the same
    >>> import json
    >>> a = union_copy(a, b)
    >>> json.dumps(a, sort_keys=True)
    '{"a": {"b": {"c": 1, "d": 2}}, "e": [1, 2]}'
    >>> json.dumps(b, sort_keys=True)
    '{"a": {"b": {"d": 2}}, "e": [1, 2]}'
    >>> a['e'][0] = 3
    >>> json.dumps(a, sort_keys=True)
    '{"a": {"b": {"c": 1, "d": 2}}, "e": [3, 2]}'
    >>> json.dumps(b, sort_keys=True)
    '{"a": {"b": {"d": 2}}, "e": [1, 2]}'
    """
    return _union_copy(copy.deepcopy(dict1), dict2)

################################################################################
def _union_copy(dict1, dict2):
    """
    Internal wrapper to keep one level of copying out of play, for efficiency.

    Only copies data on dict2, but will alter dict1.
    """

    for key, value in dict2.items():
        if key in dict1 and isinstance(value, dict):
            dict1[key] = _union_copy(dict1[key], value)
        else:
            dict1[key] = copy.deepcopy(value)
    return dict1

################################################################################
# pylint: disable=line-too-long
def export(dict1):
    '''
    Walk `dict1` which may be mixed dict()/Dict() and export any Dict()'s to dict()

    Exporting: remove internal mapping keys (\\f$\\f) but keep split keys that are tokenized
    Original: remove internal mapping keys (\\f$\\f) and split keys that are tokenized

    see also: dictlib.original()

    >>> export(Dict(first=1, second=dict(tres=Dict(nachos=2))))
    {'first': 1, 'second': {'tres': {'nachos': 2}}}

    >>> import json
    >>> export(Dict({"ugly first": 1, "second": {"tres": Dict({"nachos":2})}}))
    {'ugly_first': 1, 'ugly first': 1, 'second': {'tres': {'nachos': 2}}}

    >>> json.dumps(Dict({"ugly first": 1, "second": {"tres": Dict({"nachos":2})}}))
    '{"ugly_first": 1, "\\\\f$\\\\fugly_first": "ugly first", "ugly first": 1, "second": {"tres": {"nachos": 2}}}'

    >>> json.dumps(export(Dict({"ugly first": 1, "second": {"tres": Dict({"nachos":2})}})))
    '{"ugly_first": 1, "ugly first": 1, "second": {"tres": {"nachos": 2}}}'
    '''
    if isinstance(dict1, Dict):
        dict1 = dict1.__export__()
    for key, value in dict1.items():
        if isinstance(value, Dict):
            dict1[key] = value.__export__()
        elif isinstance(value, dict):
            dict1[key] = export(value)
    return dict1

################################################################################
# pylint: disable=line-too-long
def original(dict1):
    """
    Walk `dict1` which may be mixed dict()/Dict() and call Dict.__original__() on
    any Dicts.

    Exporting: remove internal mapping keys (\\f$\\f) but keep split keys that are tokenized
    Original: remove internal mapping keys (\\f$\\f) and split keys that are tokenized

    see also: dictlib.original()

    >>> export(Dict(first=1, second=dict(tres=Dict(nachos=2))))
    {'first': 1, 'second': {'tres': {'nachos': 2}}}

    >>> import json
    >>> original(Dict({"ugly first": 1, "second": {"tres": Dict({"nachos":2})}}))
    {'ugly first': 1, 'second': {'tres': {'nachos': 2}}}

    >>> json.dumps(Dict({"ugly first": 1, "second": {"tres": Dict({"nachos":2})}}))
    '{"ugly_first": 1, "\\\\f$\\\\fugly_first": "ugly first", "ugly first": 1, "second": {"tres": {"nachos": 2}}}'

    >>> json.dumps(original(Dict({"ugly first": 1, "second": {"tres": Dict({"nachos":2})}})))
    '{"ugly first": 1, "second": {"tres": {"nachos": 2}}}'
    """
    if isinstance(dict1, Dict):
        dict1 = dict1.__original__()
    for key, value in dict1.items():
        if isinstance(value, Dict):
            dict1[key] = value.__original__()
        elif isinstance(value, dict):
            dict1[key] = original(value)
    return dict1

################################################################################
class Dict(dict):
    """
    Represent a dictionary in object form, while handling tokenizable keys, and
    can export to original form.  Recursive.

    Not python zen because it provides an alternate way to use dictionaries.
    But I'm okay with this, becuase it is handy.

    Limitations:

       * raises error if there is a name conflict with reserved words
       * reserves the prefix \f$\f for internal use (also raises error)
       * because of namespace conflict problems, this is a deal breaker
         for universal use--you must be cautious on what keys are input.

    There are more elegant implementations to do similar things, but this
    has better functionality and is more robust, imho.

    >>> test_dict = {"\f$\fbogus":1}
    >>> test_obj = Obj(**test_dict) # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    ValueError: Key may not begin with \\f$\\f
    >>> test_obj = Obj(copy='test') # doctest: +ELLIPSIS
    Traceback (most recent call last):
     ...
    ValueError: Key 'copy' conflicts with reserved word
    >>> test_dict = {"a":{"b":1,"ugly var!":2}, "c":3}
    >>> test_obj = Obj(**test_dict)
    >>> orig_obj = test_obj.copy() # test this later
    >>> test_obj.keys()
    dict_keys(['a', 'c'])
    >>> 'a' in test_obj
    True
    >>> for key in test_obj:
    ...     key
    'a'
    'c'
    >>> test_obj.get('c')
    3
    >>> test_obj['c']
    3
    >>> test_obj.c
    3
    >>> test_obj.c = 4
    >>> test_obj.c
    4
    >>> test_obj.a.b
    1
    >>> test_obj.a.ugly_var_
    2
    >>> test_obj.a['ugly var!']
    2
    >>> import json
    >>> json.dumps(test_obj, sort_keys=True)
    '{"a": {"\\\\f$\\\\fugly_var_": "ugly var!", "b": 1, "ugly var!": 2, "ugly_var_": 2}, "c": 4}'
    >>> test_obj.__original__() # "ugly var!" is back
    {'a': {'b': 1, 'ugly var!': 2}, 'c': 4}
    >>> test_obj.a.ugly_var_ = 10
    >>> test_obj.a.ugly_var_
    10
    >>> orig_obj.__original__()
    {'a': {'b': 1, 'ugly var!': 2}, 'c': 3}
    """

    __reserved__ = set(dir(dict) + ['dict', '__init__', '__repr__', '__export__',
                                    '__iter__', '__contains__', 'copy', 'union',
                                    '__reserved__'])

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    ############################################################################
    # pylint: disable=super-init-not-called
    def __init__(self, *args, **attrs):
        if args:
            if isinstance(args[0], zip):
                attrs = dict(args[0])
            elif isinstance(args[0], dict):
                attrs = args[0]
            else:
                raise ValueError("Bad input for dictlib.Obj - not dict or zip")

        for key in attrs:
            if key[:3] == '\f$\f':
                raise ValueError("Key may not begin with \\f$\\f")
            newkey = re.sub(r'[^a-zA-Z0-9_]', '_', key)
            if newkey in self.__reserved__:
                raise ValueError("Key '{}' conflicts with reserved word".format(newkey))

            value = attrs[key]
            if isinstance(value, dict):
                value = Obj(**value)
            setattr(self, newkey, value)
            if newkey != key: # set both
                setattr(self, '\f$\f' + newkey, key)
                setattr(self, key, value)

    ############################################################################
    def __original__(self):
        """
        Return original dictionary form, without rewritten keys
        Alternate to self.__export__()
        """
        rewrite = {}
        exported = {}
        for key in self:
            if key[:3] == '\f$\f':
                rewrite[key[3:]] = self[key]
            else:
                value = self[key]
                if isinstance(value, Obj):
                    value = value.__original__()
                exported[key] = value
        for key in rewrite:
            exported[rewrite[key]] = exported[key]
            del exported[key]

        return exported

    ############################################################################
    def __export__(self):
        """
        Export (removing internal keys) using rewritten key names, not original
        keys.  For original keys, use self.__original__()
        """
        exported = {}
        for key in self:
            if key[:3] != "\f$\f":
                value = self[key]
                if isinstance(value, Obj):
                    value = value.__export__()
                exported[key] = value
        return exported

    ############################################################################
    def copy(self):
        return Obj(**self.__original__())

    ############################################################################
    def __repr__(self):
        return str(self.__export__())

    ############################################################################
    def __deepcopy__(self, memo):
        result = Obj(**self.__original__())
        memo[id(self)] = result
        return result

# backwards compatability
Obj = Dict
