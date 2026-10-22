"""Canonical messages and preference-aware UI translation without data mutation."""
import importlib
import re
import string
import sys

CONTEXT = 'QCBlender'
_messages = None
_enum_cache = {}


def messages():
    global _messages
    if _messages is None:
        merged = {}
        for name in ('translations_ui', 'translations_nodes', 'translations_properties',
                     'translations_panels', 'translations_tooltips', 'translations_annotations', 'translations_sidebar',
                     'translations_output'):
            module = importlib.import_module('.' + name, __package__)
            for key, value in module.MESSAGES.items():
                if key in merged and merged[key] != value:
                    raise ValueError(f'Conflicting translation: {key!r}')
                merged[key] = value
        _messages = merged
    return _messages


def _language(tooltip=False):
    bpy = sys.modules.get('bpy')
    if bpy is None:
        return 'en_US'
    context = getattr(bpy, 'context', None)
    view = getattr(getattr(context, 'preferences', None), 'view', None)
    if view is None:
        return 'en_US'
    if not getattr(view, 'use_translate_tooltips' if tooltip else 'use_translate_interface', False):
        return 'en_US'
    locale = view.language
    if locale == 'DEFAULT':
        locale = bpy.app.translations.locale
    return 'zh_HANS' if locale in {'zh_HANS', 'zh_CN'} else 'en_US'


def interface_language():
    return _language()


def _canonical(message):
    catalog = messages()
    if message in catalog:
        return message
    sources = [source for source, translation in catalog.items() if translation == message]
    return sources[0] if len(sources) == 1 else message


def iface(message, **values):
    message = _canonical(message)
    result = messages().get(message, message) if _language() == 'zh_HANS' else message
    return result.format(**values) if values else result


def tip(message, **values):
    message = _canonical(message)
    result = messages().get(message, message) if _language(True) == 'zh_HANS' else message
    return result.format(**values) if values else result


def error_text(error):
    text = str(error)
    language = _language()
    catalog = messages()
    canonical = _canonical(text)
    if canonical in catalog:
        return catalog[canonical] if language == 'zh_HANS' else canonical
    pairs = list(catalog.items()) if language == 'zh_HANS' else [(value, key) for key, value in catalog.items()]
    for template, translated in pairs:
        parts = list(string.Formatter().parse(template))
        fields = [field for _, field, _, _ in parts if field is not None]
        literal_bytes = sum(len(literal.encode('utf-8')) for literal, _, _, _ in parts)
        target_bytes = sum(len(literal.encode('utf-8')) for literal, _, _, _ in string.Formatter().parse(translated))
        if not fields or min(literal_bytes, target_bytes) < 8:
            continue
        pattern = ''.join(re.escape(literal) + ('(.*?)' if field is not None else '')
                          for literal, field, _, _ in parts)
        match = re.fullmatch(pattern, text, flags=re.DOTALL)
        if match:
            values = dict(zip(fields, match.groups()))
            return ''.join(literal + (values[field] if field is not None else '')
                           for literal, field, _, _ in string.Formatter().parse(translated))
    return text


def enum_items(items):
    canonical = tuple(None if item is None else tuple(item) for item in items)
    key = (_language(), _language(True), canonical)
    if key not in _enum_cache:
        _enum_cache[key] = [None if item is None else
                           (item[0], iface(item[1]), tip(item[2]), *item[3:])
                           for item in canonical]
    return _enum_cache[key]


class _Layout:
    _containers = {'row', 'column', 'column_flow', 'grid_flow', 'box', 'split', 'menu_pie'}

    def __init__(self, layout):
        object.__setattr__(self, '_layout', layout)

    def __setattr__(self, key, value):
        setattr(self._layout, key, value)

    def __getattr__(self, key):
        value = getattr(self._layout, key)
        if not callable(value):
            return value
        def call(*args, **kwargs):
            if 'text' in kwargs and kwargs.get('translate', True):
                kwargs['text'] = iface(kwargs['text'])
                if key in {'label', 'prop', 'operator', 'menu', 'popover', 'prop_search', 'operator_menu_enum', 'prop_enum'}:
                    kwargs['translate'] = False
            result = value(*args, **kwargs)
            if key in self._containers:
                return ui_layout(result)
            if key in {'panel', 'panel_prop'}:
                return tuple(ui_layout(item) if item is not None else None for item in result)
            return result
        return call


def ui_layout(layout):
    return layout if isinstance(layout, _Layout) else _Layout(layout)


def prepare_class(cls):
    import bpy
    cls.bl_translation_context = CONTEXT
    for annotation in getattr(cls, '__annotations__', {}).values():
        if isinstance(annotation, bpy.props._PropertyDeferred):
            annotation.keywords.setdefault('translation_context', CONTEXT)


def register():
    import bpy
    catalog = {(CONTEXT, key): value for key, value in messages().items()}
    # Operator descriptions use Blender's default translation context.
    catalog.update({('*', key): value for key, value in messages().items()})
    bpy.app.translations.register(__package__, {'zh_HANS': catalog, 'zh_CN': catalog})


def unregister():
    import bpy
    bpy.app.translations.unregister(__package__)
    _enum_cache.clear()
