#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pcompile import ureg


class DottableDict(dict):
    '''Make a python dict object accessible using the dot syntax.
    '''

    def __getattr__(self, attr):
        return self[attr]

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def make_dottable_dict(d):

    if isinstance(d, dict):

        d = DottableDict(d)

        for key, value in d.items():

            if isinstance(value, dict):

                setattr(d, key, make_dottable_dict(getattr(d, key)))

            elif isinstance(value, list):

                for i, item in enumerate(value):

                    value[i] = make_dottable_dict(item)

        return d

    elif isinstance(d, list):

        for i, item in enumerate(d):

            d[i] = make_dottable_dict(item)

def serialize(d):
    '''Transform dict syntax to serialized syntax, e.g.
    {'key':'value', 'key2':'value2'} syntax to key:value,key2:value2
    '''
    import operator

    st = ''
    first = True

    sorted_d = sorted(d.items(), key=operator.itemgetter(0))

    for key, value in sorted_d:

        if not first:
            st += ';'
        st += key + ':' + value
        first = False

    return st


def unserialize(st):
    '''Transform serialized dict syntax to dict syntax, e.g.
    key:value,key2:value2 syntax to {'key':'value', 'key2':'value2'}.
    '''

    d = {}

    arr = st.split(';')

    for item in arr:

        arr = item.split(':')
        key = arr[0]
        value = arr[1]
        d[key] = value

    return d


def strip_internal(d):

    s = dict(d)

    keys = s.keys()

    for key in keys:

        if key[0] == '_':

            del s[key]

        elif isinstance(s[key], dict):

            res = strip_internal(s[key])
            if res is not None:
                s[key] = res
            else:
                del s[key]

    if s is not {}:

        return s

    else:

        return None

#print strip_internal({'a':'b', '_c':{'d':'e'}, 'f':{'g':'h','_i':'j'}})
#d = {u'_reference': u'primer_f', u'classification': {u'CHEBI': u'double-stranded_dna', u'target': u'515:16s', u'orientation': u'f'}, u'_target_concentration': u'200:nanomolar'}

def dict_to_str(d):

    dnew = {}

    for key in d:

        if isinstance(d[key], dict):

            dnew[str(key)] = dict_to_str(d[key])
        else:
            dnew[str(key)] = str(d[key])

    return dnew

def ddiff(d1, d2):
    '''compute the magnitude of the difference between to dicts, comparing
    only pint quantity elements'''

    res = {}

    for key1 in d1:

        if key1 in d2:

            if isinstance(d1[key1], ureg.Quantity) and isinstance(d2[key1], ureg.Quantity):

                res[key1] = abs(d1[key1] - d2[key1])

            elif d1[key1] == d2[key1]:

                res[key1] = d1[key1]

        else:

            res = d1[key1]

    for key2 in d2:

        if key2 not in d1:

            res[key2] = d2[key2]

    return res


def to_pint(intake):

    import re

    filt = ['unknown', 'Unknown:micromolar', 'unknown:micromolar', '?:x']

    if isinstance(intake, str) or isinstance(intake, unicode):

        '''
        if intake in filt:
            raise ValueError('Cant convert to pint a concentration that is not known: ' + intake)
        '''

        arr = str(intake).split(':')
        assert len(arr) == 2

        try:
            val = float(arr[0])
            return float(arr[0]) * ureg.parse_expression(arr[1])
        except ValueError:
            return 0*ureg.parse_expression(arr[1])

    elif isinstance(intake, ureg.Quantity):
        return intake

    else:
        return None


def pint_to_str(intake):

    if isinstance(intake, ureg.Quantity):
        res = str(intake.magnitude) + ":" + str(intake.units)
        return res
    elif isinstance(intake, str):
        return intake


from yaml import load, Loader
import os

def load_imports(d, modelsdir):
    '''Recursively load imports at fields marked import: to any depth
    '''

    if isinstance(d, dict):
        for key, value in d.items():
            if key == 'load':
                ld = load(open(os.path.join(modelsdir, value), 'r'), Loader=Loader)
                ld.update(d)
                ld.pop('load')
                d = load_imports(ld, modelsdir)
            elif isinstance(value, dict):
                d[key] = load_imports(value, modelsdir)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    value[i] = load_imports(item, modelsdir)
        return d

    elif isinstance(d, list):
        for i, item in enumerate(d):
            d[i] = load_imports(item, modelsdir)
        return d

    return d



def step_wrapper(fn):

    def wrapper(*args, **kwargs):

        from pcompile.harness import Environment
        from pcompile.harness import Reaction
        from pcompile.solution import Solution

        kwargs.update(dict(zip(fn.func_code.co_varnames, args)))
        env = kwargs['env']
        assert isinstance(env, Environment)

        rxn = kwargs['rxn']
        assert isinstance(rxn, Reaction)

        if 'inputs' in kwargs:
            inputs = kwargs['inputs']
        else:
            assert hasattr(rxn, 'inputs'), 'Reaction attempted without inputs.' + str(rxn)
            inputs = rxn.inputs
        if inputs is None:
            if rxn.inputs is None:
                inputs = []
            else:
                inputs = rxn.inputs

        for j, i in enumerate(inputs):
            if not isinstance(i, Solution):
                inputs[j] = env.db.find_by_location(i['container']['location'])
        kwargs['inputs'] = inputs

        ret = fn(**kwargs)

        # Update history object to note that this particular step was run,
        # in addition to the history that is recorded about the individual
        # operations that are performed.

        return ret

    return wrapper

def temp_to_where(temp):

    conv = {"4:celsius":"cold_4",
            "27:celsius":"ambient",
            "-20:celsius":"cold_20",
            "37:celsius":"warm_37",
            "ambient":"ambient"}

    if temp in conv:
        return conv[temp]
    else:
        return None

def div(d):
    inner=''
    if isinstance(d, list):
        for thing in d:
            inner += div(thing)
    elif isinstance(d, dict):
        for key, value in d.items():
            dictinner = '<p><b>'+key+'</b></p>'
            dictinner += div(value)
            inner += '<ul class="list-group">' + dictinner + '</ul>'
            #inner += '<p><b>'+key+'</b></p>'
            #inner += div(value)
    elif isinstance(d, str):
        inner = d
    else:
        inner += ''
    return "<li class='list-group-item'>" + inner + "</li>"

def div2(d):
    inner=''
    if isinstance(d, list):
        for thing in d:
            inner += div2(thing)
    elif isinstance(d, dict):
        for key, value in d.items():
            dictinner = '<div class="panel-heading"><h3 class="panel-title">'+key+'</h3></div>'
            dictinner += div2(value)
            inner += '<div class="panel-body">' + dictinner + '</div>'
    elif isinstance(d, str):
        inner = d
    else:
        inner += ''
    return "<div class='panel panel-primary'>" + inner + "</div>"


def html(result, path):
    out = ['<!DOCTYPE html><html lang="en"><head><!-- Latest compiled and minified CSS -->\
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">\
        <!-- Optional theme -->\
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap-theme.min.css">\
        <!-- Latest compiled and minified JavaScript -->\
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script><title>Rosalind</title>']
    out.append('</head><body><h1>Rosalind</h1>')
    for ins in result['instructions']:
        out.append(div2(ins))
    out.append('</body></html>')
    with open(path,'w') as outfile:
      outfile.write(''.join(out))


