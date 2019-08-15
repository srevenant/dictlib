Dictlib is a lightweight add-on for dictionaries, primarily focused on:

  * Minimal changes/efficiency
  * *Dictionary union* done properly: `union()` (not immutably safe), `union_copy()` (immutably safe)
  * *Dot notation for retrieval* from classic dictionaries, with a string key: `dig()`, `dig_get()`, `dug()`
  * *dictionary keys as object attributes* (easy classes): `Dict()` (useful for rapid prototyping,
    just define your class as a Dict, either way:

```python
NewClass = Dict
class NewClass(Dict):
  pass
```

`union()` and `union_copy()`
===============

```python
from dictlib import union, union_copy
dict1 = union(dict1, dict2)
dict3 = union_copy(dict1, dict2)
```

Deep union of dict2 into dict1, where dictionary values are recursively merged.
Non-dictionary elements are replaced, with preference given to dict2.

This alters dict1, which is the returned result, but it will have references to
both dictionaries.  If you do not want this, use union_copy(), which is less
efficient but data-safe.

`dig()` and `dig_get()`
=============

Recursively pull from a dictionary, using dot notation.  dig_get behaves like `dict.get()`, but with dot-notated keys.

```python
from dictlib import dig, dig_get
dict1 = {"a":{"b":{"c":1},"d":[{"e":1},{"f":2}]}}
dig(dict1, "a.b.c")
# 1

dig(dict1, "a.d[1].f")
# 2

dig(dict1, "a.b.z")
# KeyError: 'z'

dig_get(dict1, "a.b.z")
# None

dig_get(dict1, "a.b.z", 2)
# 2
```

`dug()`
=============

Inverse of `dig()`, `dug()` puts an item into a nested dictionary, using dot notation.
This does not behave immutably, as it alters the origin dictionary.  

```python
from dictlib import dug
dict1 = {"a":{"b":{"c":1}}}
dug(dict1, "a.b.c", 200)
# {'a': {'b': {'c': 200}}}

# and it will instantiate dictionaries as values if the key doesn't exist:
dug(dict1, "a.b.z.e", True)
# {'a': {'b': {'c': 200, 'z': {'e': True}}}}
```

Note: dug() does not support pushing to lists within a dictionary, it assumes
all values are dictionaries in your dot notation string.  If you attempt to use
a list index, it still behaves as if it were a dictionary, which may give you
unexpected results:

```python
dict1 = {"a":{"b":{"c":1}}}
dug(dict1, "a.b.d[0].e", True)
# {'a': {'b': {'c': 1, 'd': {0: {'e': True}}}}}
```

(PR's to finish this feature correctly are appreciated)

`Dict()`
=============

A bit of sugar to represent a dictionary in object form where keys are set as
attributes on the object.  Features:

* it tokenizes your keys if they are not python safe (`"this-key"` is `.this_key`).  Example:
```python
d = Dict({"this key": "value"})
d["this-key"]
# "value"
d.this_key
# "value"
```
* Recursive -- it will walk the full depth of the dictionary

This is not python zen because it provides an alternate way to use dictionaries,
and it has some challenges with names that collide with builtin methods, but it
is very

But I'm okay with this, because it is handy bit of sugar.

Limitations:

* raises error if there is a name conflict with reserved words
* reserves the key prefix \f$\f for internal use (raises error)
* because of namespace conflict problems, you must be cautious on what keys are input
* Two keys exist for each non-tokenized name, such as `ugly var!`,
  which is tokenized to `ugly_var_`.  However, they do not point to the same
  data value!  While both exist, if exporting to original object *only* the
  value of the tokenized name is used (see examples)

```python
from dictlib import Dict
Dict(key1=1, a=2)
# {'key1': 1, 'a': 2}

test_dict = {"a":{"b":1,"ugly var!":2}, "c":3}
test_obj = Dict(**test_dict)
test_obj.keys()
# ['a', 'c']

'a' in test_obj
# True
test_obj.get('c')
# 3
test_obj['c']
# 3
test_obj.c
# 3
test_obj.c = 4
test_obj.c
# 4
test_obj.a.b
# 1
test_obj.a.ugly_var_
# 2
test_obj.a['ugly var!']
# 2

# however, these are distinctly different values, don't be confused:
test_obj.a.ugly_var_ = 0xdeadbeef
test_obj.a.ugly_var_
# 3735928559
test_obj.a['ugly var!']
# 2

# how it looks -- in most cases it tries to look normal for you, but you can
# use __export__ and __original__ to be assured. In some cases you can see the
# mapping keys, which is confusing, and needs to be fixed (PR appreciated):
test_obj = Dict(test_dict)
test_obj
# {'a': {'b': 1, 'ugly_var_': 2, 'ugly var!': 2}, 'c': 3}
import json
json.dumps(test_obj)
# '{"a": {"b": 1, "ugly_var_": 2, "\\f$\\fugly_var_": "ugly var!", "ugly var!": 2}, "c": 3}'

json.dumps(test_obj.__export__()) # removes key mapping values, but keeps split tokenized keys
# '{"a": {"b": 1, "ugly_var_": 2, "ugly var!": 2}, "c": 3}'

json.dumps(test_obj.__original__()) # removes key mapping values and tokenized keys
# '{"a": {"b": 1, "ugly var!": 2}, "c": 3}'

test_obj.__original__()
# {'a': {'b': 1, 'ugly var!': 2}, 'c': 3}
```

Note: `Dict()` was previously `Obj()`, which has been deprecated but is still supported.

`dictlib.export()` and `dictlib.original()`
======

Walk `dict1` which may be mixed dict()/Dict() and export any Dict()'s to dict(),
using the `Dict.__export__()` or `Dict.__original__()` method, respectively.

(useful for data conversions, such as with dict->yaml)

```python
dictlib.export(dictlib.Dict(first=1, second=dict(tres=dictlib.Dict(nachos=2))))
{'first': 1, 'second': {'tres': {'nachos': 2}}}
```
