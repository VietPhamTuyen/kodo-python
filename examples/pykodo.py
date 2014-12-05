import kodo
import re


def split_upper_case(s):
    return [a for a in re.split(r'([A-Z][a-z]*\d*)', s) if a]


def __get_stacks():
    result = {}
    for stack in dir(kodo):
        if stack.startswith('__'):
            continue

        stack_pieces = split_upper_case(stack)
        trace = 'no_trace'
        if stack_pieces[-1] == 'Trace':
            trace = 'trace'
            stack_pieces.pop()
        field = stack_pieces.pop().lower()

        if stack_pieces[-1] != "Factory":
            continue
        stack_pieces.pop()
        coder_type = stack_pieces.pop().lower()

        algorithm = "_".join(stack_pieces).lower()

        if algorithm not in result:
            result[algorithm] = {}
        if field not in result[algorithm]:
            result[algorithm][field] = {}
        if coder_type not in result[algorithm][field]:
            result[algorithm][field][coder_type] = {}

        result[algorithm][field][coder_type][trace] = getattr(kodo, stack)
    return result


__kodo_stacks = __get_stacks()

for algorithm in __kodo_stacks:
    globals()[algorithm] = algorithm

for field in __kodo_stacks.items()[0][1]:
    globals()[field] = field

globals()['trace'] = True
globals()['no_trace'] = False


def decoder_factory(algorithm, field, max_symbols, max_symbol_size,
                    trace=False):
    trace = 'trace' if trace else 'no_trace'
    return __kodo_stacks[algorithm][field]['decoder'][trace](
        max_symbols, max_symbol_size)


def encoder_factory(algorithm, field, max_symbols, max_symbol_size,
                    trace=False):
    trace = 'trace' if trace else 'no_trace'
    return __kodo_stacks[algorithm][field]['encoder'][trace](
        max_symbols, max_symbol_size)
