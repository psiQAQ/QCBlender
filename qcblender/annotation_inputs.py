"""Bounded, distinct source-number edits for annotation dialogs."""


def resize_numbers(numbers, count, atom_count):
    if atom_count < 1:
        raise ValueError('The source geometry has no atoms')
    if len(set(numbers)) != len(numbers) or any(not 1 <= n <= atom_count for n in numbers):
        raise ValueError('Choose distinct, existing source atom numbers')
    count = min(atom_count, max(1, int(count)))
    result = list(numbers[:count])
    used = set(result)
    for number in range(1, atom_count + 1):
        if len(result) == count:
            break
        if number not in used:
            result.append(number)
            used.add(number)
    return result


def edit_numbers(previous, proposed, atom_count):
    """Clamp each changed number, rejecting collisions without skipping a number."""
    if len(previous) != len(proposed):
        raise ValueError('Annotation input count changed during a number edit')
    if atom_count < 1 or len(set(previous)) != len(previous) or any(not 1 <= n <= atom_count for n in previous):
        raise ValueError('Choose distinct, existing source atom numbers')
    result = list(previous)
    for index, number in enumerate(proposed):
        bounded = min(atom_count, max(1, int(number)))
        if bounded not in result[:index] + result[index + 1:]:
            result[index] = bounded
    return result
