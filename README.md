Various tools, including: 

# union

	>>> dict3 = dictlib.union(dict1, dict2)
	>>> dict3 = dictlib.union_copy(dict1, dict2)

Deep union of dict2 into dict1, where dictionary values are recursively merged.
Non-dictionary elements are replaced, with preference given to dict2.

This alters dict1, which is the returned result, but it will have references to
both dictionaries.  If you do not want this, use union_copy(), which is less
efficient but data-safe.

# dig

Recursively pull from a dictionary, using dot notation.

	>>> dictlib.dig({"a":{"b":{"c":1}}}, "a.b.c")
	1
	>>> dictlib.dig({"a":{"b":{"c":1}}}, "a.b.d")
	Traceback:...

There is dig_get(), which behaves like dict.get (allows a default):

	>>> dictlib.dig_get({"a":{"b":{"c":1}}}, "a.b.c", 2)
	1
	>>> dictlib.dig_get({"a":{"b":{"c":1}}}, "a.b.d", 2)
	2

# Obj

Represent a dictionary in object form, while handling tokenizable keys, and
can export to original form.  Recursive.

Not python zen because it provides an alternate way to use dictionaries.
But I'm okay with this, becuase it is handy.

Limitations:

* raises error if there is a name conflict with reserved words
* reserves the prefix \f$\f for internal use (raises error)
* because of namespace conflict problems, this is a deal breaker for universal use--you must be cautious on what keys are input.

    >>> test_dict = {"a":{"b":1,"ugly var!":2}, "c":3}
    >>> test_obj = Obj(**test_dict)
    >>> orig_obj = test_obj.copy() # referenced later
    >>> test_obj.keys()
    ['a', 'c']
    >>> 'a' in test_obj
    True
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
    >>> test_obj.__original__()
    {'a': {'b': 1, 'ugly var!': 2}, 'c': 4}

