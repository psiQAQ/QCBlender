"""Custom-property display messages."""
from .property_labels import MESSAGES

MESSAGES = dict(MESSAGES, **{
    'External analyses require a static scientific reference; use an independent file for the corresponding step':
        '外部分析需要静态科学参考；请使用对应步骤的独立文件',
})
