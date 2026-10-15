"""Display-only descriptions for QC custom properties; stored keys are stable."""

# key | canonical label | Chinese label | canonical description | Chinese description
_ROWS = '''
qc_dataset|Dataset path|数据集路径|Path to the scientific dataset used by this object.|此对象使用的科学数据集路径。
qc_dataset_sha256|Dataset SHA-256|数据集 SHA-256|SHA-256 identity of the scientific dataset.|科学数据集的 SHA-256 标识。
qc_source_filename|Source filename|源文件名|Original input filename.|原始输入文件名。
qc_source_sha256|Source SHA-256|源文件 SHA-256|SHA-256 identity of the original input file.|原始输入文件的 SHA-256 标识。
qc_source_job|Source job|来源任务|Calculation job in the original input.|原始输入中的计算任务。
qc_view_kind|View kind|视图类型|Scientific representation used by this object.|此对象采用的科学表示类型。
qc_schema|Schema version|数据格式版本|Version of the QCBlender saved-data schema.|QCBlender 保存数据的格式版本。
qc_coordinate_unit|Coordinate unit|坐标单位|Length unit of the source coordinates.|来源坐标的长度单位。
qc_bond_source|Bond source|化学键来源|Method or source used to obtain connectivity.|化学键连接关系的来源或计算方法。
qc_calculation_status|Calculation status|计算状态|Status reported for the source calculation.|来源计算报告的状态。
qc_diagnostics|Diagnostics|诊断信息|Diagnostics retained from source parsing.|源文件解析保留的诊断信息。
qc_data_record|Data record|数据记录|Identity of the selected scientific record.|选定科学记录的标识。
qc_charge_method|Charge method|电荷方法|Population-analysis method used for atomic charges.|原子电荷采用的布居分析方法。
qc_charge_mapping|Charge mapping|电荷映射|Mapping between atomic charges and source atoms.|原子电荷与来源原子的对应关系。
qc_dipole_debye|Dipole (Debye)|偶极矩（Debye）|Dipole vector in Debye.|以 Debye 为单位的偶极矩向量。
qc_dipole_source|Dipole source|偶极矩来源|Scientific record supplying the dipole vector.|提供偶极矩向量的科学记录。
qc_mode_frequency_cm-1|Mode frequency (cm⁻¹)|振动频率（cm⁻¹）|Frequency of the selected normal mode in inverse centimetres.|选定简正模式的频率，单位为逆厘米。
qc_mode_ir_km_mol|IR intensity (km/mol)|红外强度（km/mol）|Infrared intensity of the selected normal mode.|选定简正模式的红外强度。
qc_mode_source_number|Source mode number|源模式编号|One-based normal-mode number in the source dataset.|来源数据集中从 1 开始的简正模式编号。
qc_frequency_scale|Frequency scale|频率缩放系数|Scale applied to displayed vibrational frequencies.|显示振动频率时使用的缩放系数。
qc_intensity_unit|Intensity unit|强度单位|Unit of the displayed spectral intensity.|显示的光谱强度单位。
qc_energy_selection|Energy selection|能量选择|Selected energy record.|选定的能量记录。
qc_trajectory_count|Trajectory frame count|轨迹帧数|Number of frames available in the trajectory.|轨迹包含的帧数。
qc_trajectory_frame|Trajectory frame|轨迹帧|Selected trajectory frame index.|选定的轨迹帧索引。
qc_trajectory_record|Trajectory record|轨迹记录|Saved trajectory state and source mapping.|保存的轨迹状态及来源映射。
qc_optimization_available|Optimization available|优化轨迹可用|Whether optimization records are available.|是否具有可用的优化记录。
qc_optimization_count|Optimization step count|优化步数|Number of available optimization steps.|可用的优化步数。
qc_optimization_reason|Optimization reason|优化状态说明|Explanation of optimization availability or status.|优化可用性或状态的说明。
qc_optimization_record|Optimization record|优化记录|Saved optimization state and source mapping.|保存的优化状态及来源映射。
qc_optimization_status|Optimization status|优化状态|Status of the source geometry optimization.|来源几何优化的状态。
qc_optimization_step|Optimization step|优化步|Selected geometry-optimization step.|选定的几何优化步。
qc_irc|IRC view|IRC 视图|Marks an intrinsic reaction coordinate view.|标记内禀反应坐标视图。
qc_irc_record|IRC record|IRC 记录|Saved reaction-path state and source mapping.|保存的反应路径状态及来源映射。
qc_irc_step|IRC step|IRC 步|Selected intrinsic reaction coordinate step.|选定的内禀反应坐标步。
qc_local_selection|Local selection|局部选择|Saved local atom-selection settings.|保存的局部原子选择设置。
qc_local_selection_record|Local selection record|局部选择记录|Saved atom identifiers and selection provenance.|保存的原子标识及选择来源。
qc_local_selection_attribute|Selection attribute|选择属性|Mesh attribute containing the local selection.|保存局部选择的网格属性。
qc_display_anchor|Display anchor|显示锚点|Anchor linking scientific data to a spatial view.|将科学数据关联到空间视图的锚点。
qc_result_displaystate|Result display state|结果显示状态|Saved visibility and display state for a result.|结果保存的可见性及显示状态。
qc_result_label|Result label|结果标签|Display label of the scientific result.|科学结果的显示标签。
qc_result_source_identity|Result source identity|结果来源标识|Identity linking the result to its source data.|关联结果与来源数据的标识。
qc_result_focus|Result focus|结果焦点|Saved focused result state.|保存的结果焦点状态。
qc_analysis|Analysis|分析|Scientific analysis associated with this object.|与此对象关联的科学分析。
qc_analysis_index|Analysis index|分析索引|Index of the selected analysis record.|选定分析记录的索引。
qc_analysis_role|Analysis role|分析角色|Role of this object in an analysis view.|此对象在分析视图中的角色。
qc_annotation|Annotation|标注|Scientific annotation associated with this object.|与此对象关联的科学标注。
qc_association|Association|关联|Saved association with another scientific view.|保存的与另一科学视图的关联。
qc_camera|QC camera|QC 相机|Marks a camera managed by QCBlender.|标记由 QCBlender 管理的相机。
qc_clipping|Clipping|裁剪|Saved scientific-view clipping settings.|保存的科学视图裁剪设置。
qc_color_mapping|Color mapping|颜色映射|Mapping from scientific values to colors.|科学数值到颜色的映射。
qc_color_source|Color source|颜色来源|Scientific quantity used to determine colors.|决定颜色的科学物理量。
qc_contour_child|Contour child|等值线子对象|Marks a generated contour child object.|标记生成的等值线子对象。
qc_contour_color|Contour color|等值线颜色|Display color of the contour.|等值线显示颜色。
qc_contour_enabled|Contours enabled|启用等值线|Whether contour generation is enabled.|是否启用等值线生成。
qc_contour_identity|Contour identity|等值线标识|Stable identity of the generated contour.|生成等值线的稳定标识。
qc_contour_label|Contour label|等值线标签|Display label for a contour.|等值线显示标签。
qc_contour_labels|Contour labels|等值线标签集|Saved contour label settings.|保存的等值线标签设置。
qc_contour_level|Contour level|等值线数值|Scientific value represented by this contour.|此等值线表示的科学数值。
qc_contour_levels|Contour levels|等值线数值集|Scientific values used to generate contours.|用于生成等值线的科学数值。
qc_contour_owner|Contour owner|等值线所属对象|Object that owns the generated contour.|生成等值线所属的对象。
qc_contour_restore_render|Contour render restoration|等值线渲染恢复状态|Previous contour render visibility retained for restoration.|供恢复使用的先前等值线渲染可见性。
qc_contour_restore_viewport|Contour viewport restoration|等值线视口恢复状态|Previous contour viewport visibility retained for restoration.|供恢复使用的先前等值线视口可见性。
qc_contour_source|Contour source|等值线来源|Scientific field used to generate contours.|用于生成等值线的科学场。
qc_contour_status|Contour status|等值线状态|Status of contour generation.|等值线生成状态。
qc_contour_width|Contour width|等值线宽度|Display width of contour lines.|等值线的显示宽度。
qc_e2_index|E2 record index|E2 记录索引|Index of the selected second-order perturbation record.|选定二阶微扰记录的索引。
qc_ets_table_dataset_sha256|ETS dataset SHA-256|ETS 数据集 SHA-256|Identity of the dataset used for the ETS table.|ETS 表使用的数据集标识。
qc_ets_table_source|ETS table source|ETS 表来源|Scientific source used for the ETS table.|ETS 表使用的科学来源。
qc_field|Field|场|Scientific scalar-field settings or identity.|科学标量场的设置或标识。
qc_fog|Fog|雾|Saved volume-fog display settings.|保存的体积雾显示设置。
qc_layer_order|Layer order|图层顺序|Display ordering of generated scientific layers.|生成的科学图层显示顺序。
qc_layer_restore_render|Layer render restoration|图层渲染恢复状态|Previous layer render visibility retained for restoration.|供恢复使用的先前图层渲染可见性。
qc_layer_restore_viewport|Layer viewport restoration|图层视口恢复状态|Previous layer viewport visibility retained for restoration.|供恢复使用的先前图层视口可见性。
qc_legend|Legend|图例|Scientific legend settings.|科学图例设置。
qc_legend_layout|Legend layout|图例布局|Saved arrangement of legend elements.|保存的图例元素布局。
qc_mayer_display_pair|Mayer atom pair|Mayer 原子对|Atom pair selected for Mayer bond-order display.|选定用于显示 Mayer 键级的原子对。
qc_mayer_display_values|Mayer values|Mayer 数值|Mayer bond-order values used for display.|用于显示的 Mayer 键级数值。
qc_mayer_pair_index|Mayer pair index|Mayer 原子对索引|Index of the selected Mayer atom pair.|选定 Mayer 原子对的索引。
qc_measurement|Measurement|测量|Saved geometric measurement settings and atom identities.|保存的几何测量设置及原子标识。
qc_nbo_index|NBO record index|NBO 记录索引|Index of the selected natural bond orbital record.|选定自然键轨道记录的索引。
qc_negative|Negative branch|负值分支|Marks the negative branch of a signed scalar field.|标记有符号标量场的负值分支。
qc_opacity|Opacity|不透明度|Display opacity of the scientific representation.|科学表示的显示不透明度。
qc_palette|Palette|配色|Saved color-palette settings.|保存的配色设置。
qc_plane_definition|Plane definition|平面定义|Geometric definition of the scientific section plane.|科学截面平面的几何定义。
qc_probe|Probe|探针|Scientific probe settings or sampled result.|科学探针设置或采样结果。
qc_role|QC role|QC 角色|Stable internal role of this generated item.|此生成项的稳定内部角色。
qc_spectrum_label|Spectrum label|光谱标签|Display label of the spectrum.|光谱的显示标签。
qc_transfer|Transfer function|传递函数|Mapping from scientific scalar values to display properties.|科学标量值到显示属性的映射。
qc_value|Scientific value|科学数值|Scientific value represented by this item; see its source record for units.|此项表示的科学数值；单位见来源记录。
'''

LABELS = {}
MESSAGES = {}
for _line in _ROWS.strip().splitlines():
    _key, _label, _zh_label, _description, _zh_description = _line.split('|')
    LABELS[_key] = (_label, _description)
    MESSAGES[_label] = _zh_label
    MESSAGES[_description] = _zh_description
