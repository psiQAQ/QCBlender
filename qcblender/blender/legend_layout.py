"""Dimensionless legend layout coefficients for geometry nodes."""

LAYOUT = {
    'horizontal': {
        'minimum': ((-.5, 0, 0, 0), (0, -.5, -1.1875, 0)),
        'center': ((-.1, 0, 0, 0), (0, -.5, -1.1875, 0)),
        'maximum': ((.325, 0, 0, 0), (0, -.5, -1.1875, 0)),
        'title': ((-.5, 0, 0, 0), (0, .5, 0, .11)),
    },
    'vertical': {
        'minimum': ((0, .5, 0, .1), (-.5, 0, 0, 0)),
        'center': ((0, .5, 0, .1), (0, 0, -.5, 0)),
        'maximum': ((0, .5, 0, .1), (.5, 0, -1, 0)),
        'title': ((0, -.5, 0, 0), (.5, 0, 1, .1)),
    },
}


def coordinate(coefficients, length, width, text_size):
    return sum(a * b for a, b in zip(coefficients, (length, width, text_size, 1)))
