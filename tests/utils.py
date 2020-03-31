import collections
import itertools
import json
import six

def to_cmd_args(mapping):
    sorted_keys = sorted(mapping.keys())

    def arg_name(obj):
        string = obj
#        string = _decode(obj)
        if string:
            return '--%s' % string if len(string) > 1 else '-%s' % string
#            return u'--%s' % string if len(string) > 1 else u'-%s' % string
        else:
            return ''
#            return u''

    arg_names = [arg_name(argument) for argument in sorted_keys]

    def arg_value(value):
        if hasattr(value, 'items'):
            map_items = ['%s=%s' % (k, v) for k, v in sorted(value.items())]
            return ','.join(map_items)
        return value
#        return _decode(value)

    arg_values = [arg_value(mapping[key]) for key in sorted_keys]

    items = zip(arg_names, arg_values)

    return [item for item in itertools.chain.from_iterable(items)]