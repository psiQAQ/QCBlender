"""Custom-property display messages."""
from .property_labels import MESSAGES

MESSAGES = dict(MESSAGES, **{
    'Fragments contain repeated atoms; the overlap declaration is retained: {atoms}':
        '片段之间包含重复原子；已保留交叠声明：{atoms}',
    'External analyses require a static scientific reference; use an independent file for the corresponding step':
        '外部分析需要静态科学参考；请使用对应步骤的独立文件',
})
