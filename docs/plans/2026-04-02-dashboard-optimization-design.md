# 技术债务可视化仪表盘优化设计文档

**日期**: 2026-04-02
**版本**: 1.0
**作者**: Claude Code

## 概述

本文档描述了技术债务可视化仪表盘的优化设计方案。目标是通过引入现代化UI框架，增强数据可视化能力，提供更强大的交互功能和更好的用户体验。

## 设计目标

### 主要目标
增强数据可视化能力，提供更丰富的图表类型和交互功能。

### 核心功能需求
1. **更多图表类型** - 添加热力图、散点图、趋势图、树图等高级可视化
2. **数据导出和报告生成** - 支持导出PNG/PDF/Excel格式
3. **数据筛选和过滤** - 动态筛选特定类型、优先级、文件路径的债务项
4. **数据钻取和详情查看** - 点击图表元素查看详细信息

### 技术约束
- 使用原生JavaScript + UI库（无框架）
- 保持与现有Python后端的兼容性
- 无构建工具，直接通过CDN引入依赖

## 技术选型

### 前端技术栈
- **ECharts 5.5.1** - 核心可视化库
  - 支持丰富的图表类型
  - 强大的交互能力
  - 内置导出功能
  - 中文文档完善

- **Spectre.css 0.5.9** - 轻量级CSS框架
  - 仅10KB大小
  - 现代化设计风格
  - 无需JavaScript依赖

- **原生 JavaScript ES6+** - 模块化组织代码

### 后端技术栈
- **Python + dashboard.py** - 保持现有实现，生成数据并渲染HTML模板

## 整体架构

### 文件结构

```
tech-debt-mcp/
├── dashboard/
│   ├── index.html              # 主页面
│   ├── css/
│   │   ├── main.css           # 主样式（引入Spectre.css）
│   │   └── dashboard.css      # 仪表盘自定义样式
│   ├── js/
│   │   ├── app.js             # 主应用逻辑
│   │   ├── charts/
│   │   │   ├── chart-manager.js      # 图表管理器
│   │   │   ├── type-distribution.js  # 类型分布图（环形图）
│   │   │   ├── complexity-trend.js   # 复杂度趋势图（折线图）
│   │   │   ├── heatmap.js            # 文件复杂度热力图
│   │   │   └── sankey.js             # 债务流动桑基图
│   │   ├── components/
│   │   │   ├── filter-panel.js       # 筛选面板
│   │   │   ├── detail-modal.js       # 详情模态框
│   │   │   ├── export-panel.js       # 导出面板
│   │   │   └── data-table.js         # 数据表格
│   │   └── utils/
│   │       ├── data-processor.js     # 数据处理工具
│   │       └── export-utils.js       # 导出工具
│   └── assets/               # 静态资源
└── dashboard.py              # Python后端（现有）
```

### HTML模板架构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <!-- 引入Spectre.css -->
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre.min.css">
    <link rel="stylesheet" href="https://unpkg.com/spectre.css/dist/spectre-exp.min.css">
    <!-- 引入ECharts -->
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- 筛选面板 -->
        <div class="filter-panel">...</div>

        <!-- 统计卡片区域 -->
        <div class="stats-grid">...</div>

        <!-- 图表网格 -->
        <div class="charts-grid">
            <div class="chart-card" id="chart-type"></div>
            <div class="chart-card" id="chart-trend"></div>
            <div class="chart-card" id="chart-heatmap"></div>
            <div class="chart-card" id="chart-sankey"></div>
        </div>

        <!-- 数据表格 -->
        <div class="data-table-container">...</div>
    </div>

    <!-- 详情模态框 -->
    <div class="modal" id="detail-modal">...</div>

    <!-- 导出面板 -->
    <div class="export-panel">...</div>

    <!-- JavaScript模块 -->
    <script type="module" src="/js/app.js"></script>
</body>
</html>
```

## 页面布局设计

### 桌面端布局（>=1200px）

```
┌─────────────────────────────────────────────────────────────┐
│  标题栏：技术债务分析报告                     [导出] [刷新]  │
├─────────────────────────────────────────────────────────────┤
│  筛选面板（可折叠）                                          │
│  [类型 ▼] [优先级 ▼] [文件路径搜索] [复杂度范围滑块]        │
│  [应用筛选] [重置]                                          │
├─────────────────────────────────────────────────────────────┤
│  统计卡片网格（4列）                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                      │
│  │总债务│ │高优先│ │平均复│ │总修改│                      │
│  │  42  │ │  15  │ │ 12.5 │ │ 328  │                      │
│  └──────┘ └──────┘ └──────┘ └──────┘                      │
├─────────────────────────────────────────────────────────────┤
│  图表网格（2x2布局）                                         │
│  ┌────────────────────┐ ┌────────────────────┐            │
│  │ 债务类型分布        │ │ 复杂度趋势图        │            │
│  │ （环形图）          │ │ （折线图）          │            │
│  │ 可点击钻取          │ │ 可缩放时间轴        │            │
│  └────────────────────┘ └────────────────────┘            │
│  ┌────────────────────┐ ┌────────────────────┐            │
│  │ 文件复杂度热力图    │ │ 债务流动桑基图      │            │
│  │ （树图+颜色映射）   │ │ （文件→类型流向）   │            │
│  └────────────────────┘ └────────────────────┘            │
├─────────────────────────────────────────────────────────────┤
│  数据表格（Top 20）                        [展开全部]        │
│  序号 | 类型 | 文件 | 实体 | 复杂度 | 债务指数 | 优先级      │
│  ────────────────────────────────────────────────────────  │
│   1  | 复杂方法 | File1.java | processData | 25 | 0.85 | 高│
│   2  | 长方法   | File2.py   | longMethod  | 15 | 0.72 | 高│
│  ────────────────────────────────────────────────────────  │
│  [上一页] 1 2 3 ... [下一页]      显示 1-20 / 共 42 条     │
└─────────────────────────────────────────────────────────────┘
```

### 响应式布局规则

**平板端（768px-1199px）**：
- 统计卡片：2x2网格
- 图表区域：1列垂直排列
- 表格：可折叠详情列

**移动端（<768px）**：
- 统计卡片：1列垂直堆叠
- 图表：1列，高度自适应
- 表格：卡片式展示，关键信息优先

### 交互设计

**筛选面板**：
- 默认展开，可通过按钮折叠/展开
- 筛选条件变化时，图表和表格实时更新（防抖500ms）
- "重置"按钮恢复所有筛选条件

**图表交互**：
- 所有图表支持鼠标悬停显示tooltip
- 点击图表元素触发钻取操作
- 图表右上角提供"放大"、"下载PNG"工具按钮
- 支持图表联动（点击一个图表，其他图表高亮相关数据）

**表格交互**：
- 点击表头排序
- 点击行展开详情面板（右侧滑出）
- 支持多选导出

**导出功能**：
- 顶部固定导出按钮，点击展开导出面板
- 支持导出格式：PNG（图表）、Excel（数据）、PDF（完整报告）
- 导出时显示进度条

## 功能组件设计

### 1. 筛选面板组件

**功能**：
- 类型筛选（多选下拉框）
- 优先级筛选（高/中/低，单选）
- 文件路径搜索（模糊匹配输入框）
- 复杂度范围滑块（双滑块选择范围）
- 应用筛选按钮 + 重置按钮

**实现方式**：
```javascript
class FilterPanel {
    constructor(containerId, onFilterChange) {
        this.container = document.getElementById(containerId);
        this.filters = {
            types: [],
            priority: null,
            filePath: '',
            complexityRange: [0, 100]
        };
        this.onFilterChange = onFilterChange;
        this.init();
    }

    // 防抖处理，避免频繁更新
    debounceFilter = _.debounce(() => {
        this.onFilterChange(this.filters);
    }, 500);
}
```

### 2. 图表组件

#### 2.1 债务类型分布图（环形图）

**功能**：
- 显示各类型债务的占比
- 点击扇区钻取该类型的详细信息
- 悬停显示类型名称、数量、百分比

**ECharts配置**：
```javascript
{
    series: [{
        type: 'pie',
        radius: ['40%', '70%'],  // 环形图
        avoidLabelOverlap: false,
        itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
        },
        label: {
            show: true,
            formatter: '{b}: {c} ({d}%)'
        },
        emphasis: {
            label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold'
            }
        }
    }]
}
```

#### 2.2 复杂度趋势图（折线图）

**功能**：
- 显示Top 10文件/方法的复杂度对比
- 可切换查看不同时间点的复杂度变化
- 支持缩放和平移

**ECharts配置**：
```javascript
{
    xAxis: {
        type: 'category',
        data: fileNames
    },
    yAxis: {
        type: 'value',
        name: '复杂度'
    },
    series: [{
        type: 'line',
        smooth: true,
        data: complexityValues,
        areaStyle: {  // 区域填充
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(54, 162, 235, 0.5)' },
                { offset: 1, color: 'rgba(54, 162, 235, 0.1)' }
            ])
        }
    }],
    dataZoom: [{  // 支持缩放
        type: 'inside',
        start: 0,
        end: 100
    }]
}
```

#### 2.3 文件复杂度热力图（树图）

**功能**：
- 以树状结构展示文件目录层级
- 颜色深浅表示复杂度高低
- 矩形大小表示代码行数
- 点击文件钻取详情

**ECharts配置**：
```javascript
{
    series: [{
        type: 'treemap',
        data: fileTreeData,
        roam: false,
        nodeClick: 'link',  // 点击跳转详情
        breadcrumb: {
            show: true
        },
        label: {
            show: true,
            formatter: '{b}\n{c}'
        },
        itemStyle: {
            borderColor: '#fff',
            borderWidth: 1,
            gapWidth: 1
        }
    }]
}
```

#### 2.4 债务流动桑基图（Sankey）

**功能**：
- 展示文件/模块与债务类型的对应关系
- 流向粗细表示债务数量
- 可视化债务分布模式

**ECharts配置**：
```javascript
{
    series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: {
            focus: 'adjacency'
        },
        data: nodes,
        links: links,
        lineStyle: {
            color: 'gradient',
            curveness: 0.5
        }
    }]
}
```

### 3. 数据表格组件

**功能**：
- 显示Top 20债务项
- 支持排序（复杂度、债务指数、优先级）
- 分页功能
- 点击行展开详情面板
- 多选支持批量导出

**实现方式**：
```javascript
class DataTable {
    constructor(containerId, data) {
        this.container = document.getElementById(containerId);
        this.data = data;
        this.currentPage = 1;
        this.pageSize = 20;
        this.sortColumn = 'debt_score';
        this.sortOrder = 'desc';
        this.selectedRows = new Set();
    }

    renderTable() {
        const paginatedData = this.getPaginatedData();
        const html = this.generateTableHTML(paginatedData);
        this.container.innerHTML = html;
        this.bindEvents();
    }
}
```

### 4. 详情模态框组件

**功能**：
- 展示单个债务项的完整信息
- 包含：基本信息、复杂度详情、修改历史、AI建议
- 提供快速操作按钮（标记已处理、导出）

**布局**：
```
┌─────────────────────────────────────┐
│  债务详情                    [关闭] │
├─────────────────────────────────────┤
│  基本信息                            │
│  • 类型：复杂方法                    │
│  • 文件：/path/to/File.java          │
│  • 实体：processData                 │
│  • 复杂度：25                        │
│  • 债务指数：0.85                    │
│  • 优先级：高                        │
├─────────────────────────────────────┤
│  AI重构建议                          │
│  "建议将此方法拆分为3个子方法..."    │
├─────────────────────────────────────┤
│  修改历史（最近5次）                 │
│  • 2024-03-15 - 修改复杂度逻辑      │
│  • 2024-02-20 - 新增参数校验        │
│  └─────────────────────────────────┘
│  [导出此项] [标记已处理]             │
└─────────────────────────────────────┘
```

### 5. 导出面板组件

**功能**：
- 选择导出格式（PNG/Excel/PDF）
- 选择导出范围（当前筛选结果/全部数据）
- 导出进度显示
- 下载链接生成

**实现方式**：
- PNG：使用ECharts内置的`getDataURL()`方法
- Excel：使用SheetJS库（CDN引入）
- PDF：使用jsPDF库（CDN引入）

## 数据流与状态管理

### 数据流架构

```
┌─────────────────────────────────────────────────────────┐
│  Python Backend (dashboard.py)                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 生成数据：analyze_tech_debt()                    │   │
│  │ 输出：{ items: [...], stats: {...} }            │   │
│  └─────────────────────────────────────────────────┘   │
│            ↓ JSON序列化                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 渲染HTML模板，注入数据：window.dashboardData    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────┐
│  Frontend (JavaScript)                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │ App State (状态管理)                             │   │
│  │ - rawData: 完整原始数据                          │   │
│  │ - filteredData: 筛选后数据                       │   │
│  │ - filters: 当前筛选条件                          │   │
│  │ - selectedItems: 已选项目                        │   │
│  └─────────────────────────────────────────────────┘   │
│            ↓                                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Data Processor (数据处理器)                      │   │
│  │ - filterData(): 应用筛选条件                     │   │
│  │ - sortData(): 排序数据                          │   │
│  │ - aggregateData(): 聚合统计                     │   │
│  │ - transformForChart(): 图表数据转换             │   │
│  └─────────────────────────────────────────────────┘   │
│            ↓                                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Renderers (渲染器)                               │   │
│  │ - ChartManager: 更新所有图表                     │   │
│  │ - DataTable: 更新表格                           │   │
│  │ - StatsCards: 更新统计卡片                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 状态管理模式

```javascript
// app.js - 主应用状态管理
class DashboardApp {
    constructor() {
        this.state = {
            rawData: [],           // 原始数据（不变）
            filteredData: [],      // 筛选后数据
            filters: {             // 当前筛选条件
                types: [],
                priority: null,
                filePath: '',
                complexityRange: [0, 100]
            },
            ui: {                  // UI状态
                filterPanelCollapsed: false,
                selectedItemId: null,
                currentPage: 1,
                sortColumn: 'debt_score',
                sortOrder: 'desc'
            }
        };

        this.components = {
            filterPanel: null,
            chartManager: null,
            dataTable: null,
            detailModal: null,
            exportPanel: null
        };

        this.init();
    }

    // 更新状态并触发渲染
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }

    // 主渲染方法
    render() {
        // 1. 应用筛选
        this.state.filteredData = DataProcessor.filterData(
            this.state.rawData,
            this.state.filters
        );

        // 2. 更新统计卡片
        this.updateStats();

        // 3. 更新图表
        this.components.chartManager.updateCharts(this.state.filteredData);

        // 4. 更新表格
        this.components.dataTable.updateData(this.state.filteredData);
    }
}
```

### 数据处理流程

#### 初始化流程

```javascript
// 页面加载时
document.addEventListener('DOMContentLoaded', () => {
    // 1. 从window.dashboardData获取Python注入的数据
    const rawData = window.dashboardData || [];

    // 2. 初始化应用
    const app = new DashboardApp();
    app.setState({ rawData });

    // 3. 初始化组件
    app.components.filterPanel = new FilterPanel('filter-panel', app.handleFilterChange.bind(app));
    app.components.chartManager = new ChartManager(app.state.filteredData);
    app.components.dataTable = new DataTable('data-table', app.state.filteredData);
    app.components.detailModal = new DetailModal('detail-modal');
    app.components.exportPanel = new ExportPanel('export-panel');

    // 4. 首次渲染
    app.render();
});
```

#### 筛选流程

```javascript
// 用户更改筛选条件时
handleFilterChange(newFilters) {
    // 1. 更新筛选状态
    this.setState({
        filters: { ...this.state.filters, ...newFilters },
        ui: { ...this.state.ui, currentPage: 1 }  // 重置到第一页
    });

    // 2. 自动触发render()
}
```

#### 钻取流程

```javascript
// 点击图表元素时
handleChartDrillDown(params) {
    // 1. 获取点击的数据项
    const clickedItem = params.data;

    // 2. 显示详情模态框
    this.components.detailModal.show(clickedItem);

    // 3. 记录用户行为（可选）
    this.trackUserAction('drill_down', clickedItem.id);
}
```

#### 导出流程

```javascript
// 用户点击导出按钮时
handleExport(format, scope) {
    // 1. 获取要导出的数据
    const dataToExport = scope === 'filtered'
        ? this.state.filteredData
        : this.state.rawData;

    // 2. 根据格式调用不同的导出器
    switch(format) {
        case 'png':
            ExportUtils.exportChartsAsPNG();
            break;
        case 'excel':
            ExportUtils.exportDataAsExcel(dataToExport);
            break;
        case 'pdf':
            ExportUtils.exportAsPDF(dataToExport);
            break;
    }
}
```

### 数据转换示例

```javascript
// utils/data-processor.js
class DataProcessor {
    // 筛选数据
    static filterData(data, filters) {
        return data.filter(item => {
            // 类型筛选
            if (filters.types.length > 0 && !filters.types.includes(item.type)) {
                return false;
            }

            // 优先级筛选
            if (filters.priority && item.priority !== filters.priority) {
                return false;
            }

            // 文件路径搜索
            if (filters.filePath && !item.file_path.includes(filters.filePath)) {
                return false;
            }

            // 复杂度范围筛选
            if (item.complexity < filters.complexityRange[0] ||
                item.complexity > filters.complexityRange[1]) {
                return false;
            }

            return true;
        });
    }

    // 聚合统计
    static aggregateStats(data) {
        return {
            totalItems: data.length,
            highPriority: data.filter(i => i.debt_score >= 0.5).length,
            avgComplexity: data.reduce((sum, i) => sum + i.complexity, 0) / data.length,
            totalModifications: data.reduce((sum, i) => sum + i.modification_frequency, 0)
        };
    }

    // 转换为图表数据
    static transformForPieChart(data) {
        const typeCounts = {};
        data.forEach(item => {
            typeCounts[item.type] = (typeCounts[item.type] || 0) + 1;
        });

        return Object.entries(typeCounts).map(([name, value]) => ({
            name,
            value
        }));
    }

    // 转换为树图数据
    static transformForTreeMap(data) {
        // 按文件路径构建树状结构
        const tree = {};
        data.forEach(item => {
            const pathParts = item.file_path.split('/');
            let current = tree;
            pathParts.forEach((part, index) => {
                if (!current[part]) {
                    current[part] = index === pathParts.length - 1
                        ? { value: item.complexity, item }
                        : {};
                }
                current = current[part];
            });
        });

        return this.buildTreeData(tree);
    }
}
```

## 错误处理

### 数据加载错误

```javascript
// 数据加载失败处理
class DashboardApp {
    async loadData() {
        try {
            // 检查数据是否存在
            if (!window.dashboardData || !Array.isArray(window.dashboardData)) {
                throw new Error('数据格式不正确');
            }

            // 验证数据结构
            this.validateData(window.dashboardData);

            this.setState({ rawData: window.dashboardData });
        } catch (error) {
            this.showError('数据加载失败', error.message);
            this.showEmptyState();
        }
    }

    validateData(data) {
        const requiredFields = ['type', 'file_path', 'entity_name', 'complexity'];
        data.forEach((item, index) => {
            requiredFields.forEach(field => {
                if (!(field in item)) {
                    console.warn(`数据项 ${index} 缺少字段: ${field}`);
                }
            });
        });
    }

    showError(title, message) {
        // 使用Spectre.css的toast组件显示错误
        const toast = document.createElement('div');
        toast.className = 'toast toast-error';
        toast.innerHTML = `
            <button class="btn btn-clear float-right"></button>
            <h5>${title}</h5>
            <p>${message}</p>
        `;
        document.body.appendChild(toast);

        setTimeout(() => toast.remove(), 5000);
    }

    showEmptyState() {
        // 显示空状态占位符
        document.getElementById('main-container').innerHTML = `
            <div class="empty">
                <div class="empty-icon">
                    <i class="icon icon-4x icon-stop"></i>
                </div>
                <p class="empty-title h5">暂无数据</p>
                <p class="empty-subtitle">请先运行技术债务分析</p>
            </div>
        `;
    }
}
```

### 图表渲染错误

```javascript
class ChartManager {
    createChart(containerId, options) {
        try {
            const chart = echarts.init(document.getElementById(containerId));
            chart.setOption(options);
            return chart;
        } catch (error) {
            console.error(`图表初始化失败: ${containerId}`, error);
            this.showChartError(containerId, error.message);
            return null;
        }
    }

    showChartError(containerId, message) {
        const container = document.getElementById(containerId);
        container.innerHTML = `
            <div class="empty" style="height: 300px; display: flex; align-items: center; justify-content: center;">
                <p class="text-error">图表加载失败: ${message}</p>
            </div>
        `;
    }
}
```

### 用户操作错误

```javascript
class ExportPanel {
    async handleExport(format) {
        try {
            // 验证数据
            if (this.data.length === 0) {
                throw new Error('没有可导出的数据');
            }

            // 执行导出
            await ExportUtils.export(this.data, format);

            this.showSuccess('导出成功');
        } catch (error) {
            this.showError('导出失败', error.message);
        }
    }
}
```

## 性能优化

### 大数据量优化

```javascript
class DashboardApp {
    // 虚拟滚动（表格大数据量）
    enableVirtualScroll() {
        const tableBody = document.querySelector('.data-table tbody');
        const rowHeight = 48;
        const visibleRows = 20;

        // 只渲染可见行
        const renderVisibleRows = () => {
            const scrollTop = tableBody.scrollTop;
            const startIndex = Math.floor(scrollTop / rowHeight);
            const endIndex = Math.min(startIndex + visibleRows, this.data.length);

            this.renderRows(startIndex, endIndex);
        };

        tableBody.addEventListener('scroll', renderVisibleRows);
    }

    // 图表数据采样（超过1000个点时）
    sampleChartData(data, maxPoints = 500) {
        if (data.length <= maxPoints) return data;

        const step = Math.ceil(data.length / maxPoints);
        return data.filter((_, index) => index % step === 0);
    }
}
```

### 渲染性能优化

```javascript
class ChartManager {
    // 防抖更新（筛选条件变化时）
    debouncedUpdate = _.debounce((data) => {
        this.updateCharts(data);
    }, 300);

    // 图表懒加载
    lazyLoadCharts() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const chartId = entry.target.id;
                    this.renderChart(chartId);
                    observer.unobserve(entry.target);
                }
            });
        });

        document.querySelectorAll('.chart-container').forEach(container => {
            observer.observe(container);
        });
    }

    // 增量更新（而非完全重新渲染）
    updateChartPartial(chartId, newData) {
        const chart = this.charts[chartId];
        if (!chart) return;

        // 使用setOption的notMerge模式
        chart.setOption({
            series: [{ data: newData }]
        }, { notMerge: false, lazyUpdate: true });
    }
}
```

### 内存优化

```javascript
class DashboardApp {
    // 清理未使用的图表实例
    destroyUnusedCharts() {
        const visibleChartIds = this.getVisibleChartIds();
        Object.keys(this.charts).forEach(chartId => {
            if (!visibleChartIds.includes(chartId)) {
                this.charts[chartId].dispose();
                delete this.charts[chartId];
            }
        });
    }

    // 页面卸载时清理
    beforeUnload() {
        window.addEventListener('beforeunload', () => {
            // 销毁所有图表实例
            Object.values(this.charts).forEach(chart => chart.dispose());

            // 清理事件监听器
            this.eventListeners.forEach(listener => {
                listener.element.removeEventListener(listener.event, listener.handler);
            });
        });
    }
}
```

### 网络优化

```javascript
// CDN资源加载失败降级方案
function loadScriptWithFallback(primaryUrl, fallbackUrl) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = primaryUrl;
        script.onload = resolve;
        script.onerror = () => {
            console.warn(`${primaryUrl} 加载失败，使用备用地址`);
            script.src = fallbackUrl;
        };
        document.head.appendChild(script);
    });
}

// 使用示例
loadScriptWithFallback(
    'https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js',
    'https://unpkg.com/echarts@5.5.1/dist/echarts.min.js'
).then(() => {
    app.init();
});
```

## 测试策略

### 单元测试

```javascript
// 测试数据处理逻辑
describe('DataProcessor', () => {
    test('filterData - 应正确筛选类型', () => {
        const data = [
            { type: 'complex_method', complexity: 10 },
            { type: 'long_method', complexity: 15 }
        ];

        const filters = { types: ['complex_method'] };
        const result = DataProcessor.filterData(data, filters);

        expect(result).toHaveLength(1);
        expect(result[0].type).toBe('complex_method');
    });

    test('aggregateStats - 应正确计算统计数据', () => {
        const data = [
            { debt_score: 0.6, complexity: 10, modification_frequency: 5 },
            { debt_score: 0.4, complexity: 20, modification_frequency: 3 }
        ];

        const stats = DataProcessor.aggregateStats(data);

        expect(stats.totalItems).toBe(2);
        expect(stats.highPriority).toBe(1);
        expect(stats.avgComplexity).toBe(15);
        expect(stats.totalModifications).toBe(8);
    });
});
```

### 集成测试

```javascript
// 测试组件交互
describe('DashboardApp Integration', () => {
    let app;

    beforeEach(() => {
        // 设置测试数据
        window.dashboardData = mockData;
        app = new DashboardApp();
    });

    test('筛选条件变化应更新图表和表格', () => {
        // 触发筛选
        app.handleFilterChange({ types: ['complex_method'] });

        // 验证数据已更新
        expect(app.state.filteredData.length).toBeLessThan(app.state.rawData.length);

        // 验证图表已更新
        const chartData = app.components.chartManager.charts['typeChart'].getOption();
        expect(chartData.series[0].data).toHaveLength(1);

        // 验证表格已更新
        const tableRows = document.querySelectorAll('.data-table tbody tr');
        expect(tableRows.length).toBe(app.state.filteredData.length);
    });

    test('点击图表应打开详情模态框', () => {
        // 模拟点击图表
        const chart = app.components.chartManager.charts['typeChart'];
        chart.dispatchAction({
            type: 'click',
            seriesIndex: 0,
            dataIndex: 0
        });

        // 验证模态框已打开
        const modal = document.getElementById('detail-modal');
        expect(modal.classList.contains('active')).toBe(true);
    });
});
```

### 性能测试

```javascript
// 测试大数据量渲染性能
describe('Performance Tests', () => {
    test('1000条数据筛选应在300ms内完成', () => {
        const bigData = generateMockData(1000);
        const app = new DashboardApp();
        app.setState({ rawData: bigData });

        const startTime = performance.now();
        app.handleFilterChange({ types: ['complex_method'] });
        const endTime = performance.now();

        expect(endTime - startTime).toBeLessThan(300);
    });

    test('图表更新应在100ms内完成', () => {
        const chartManager = new ChartManager();
        const data = generateMockData(100);

        const startTime = performance.now();
        chartManager.updateCharts(data);
        const endTime = performance.now();

        expect(endTime - startTime).toBeLessThan(100);
    });
});
```

### E2E测试（Playwright/Puppeteer示例）

```javascript
// 测试完整用户流程
describe('E2E: User Workflow', () => {
    test('用户应能完成筛选->查看详情->导出的完整流程', async () => {
        // 1. 访问页面
        await page.goto('http://localhost:8080/dashboard');

        // 2. 应用筛选
        await page.selectOption('#type-filter', 'complex_method');
        await page.click('#apply-filter');

        // 3. 验证图表更新
        await page.waitForSelector('#typeChart canvas');
        const chartVisible = await page.isVisible('#typeChart canvas');
        expect(chartVisible).toBe(true);

        // 4. 点击图表元素
        await page.click('#typeChart canvas', { position: { x: 100, y: 100 } });

        // 5. 验证详情模态框
        await page.waitForSelector('#detail-modal.active');
        const modalVisible = await page.isVisible('#detail-modal.active');
        expect(modalVisible).toBe(true);

        // 6. 导出数据
        await page.click('#export-btn');
        await page.click('#export-excel');

        // 7. 验证下载
        const download = await page.waitForEvent('download');
        expect(download.suggestedFilename()).toMatch(/tech-debt.*\.xlsx/);
    });
});
```

## 部署与监控

### 部署检查清单

- [ ] 所有CDN资源使用HTTPS
- [ ] 添加资源完整性校验（SRI）
- [ ] 启用浏览器缓存（Cache-Control）
- [ ] 压缩JavaScript和CSS
- [ ] 图片资源使用WebP格式
- [ ] 配置错误上报

### 性能监控

```javascript
// 上报性能指标
function reportPerformance() {
    const metrics = {
        // 页面加载时间
        pageLoadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,

        // DOM渲染时间
        domRenderTime: performance.timing.domComplete - performance.timing.domLoading,

        // 首次渲染时间
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime,

        // 首次内容渲染
        firstContentfulPaint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,

        // 图表渲染时间
        chartRenderTime: window.chartRenderTime
    };

    // 发送到监控服务
    navigator.sendBeacon('/api/metrics', JSON.stringify(metrics));
}

// 页面加载完成后上报
window.addEventListener('load', () => {
    setTimeout(reportPerformance, 1000);
});
```

## 总结

本设计方案通过引入ECharts可视化库和Spectre.css轻量级框架，在保持现有技术栈的基础上，大幅提升了可视化仪表盘的功能和用户体验。

### 核心优势

1. **渐进式增强** - 在现有基础上优化，风险可控
2. **功能完整** - 支持筛选、钻取、导出等高级功能
3. **性能优秀** - 虚拟滚动、懒加载、防抖等技术保证流畅体验
4. **易于维护** - 模块化设计，代码结构清晰
5. **文档完善** - 包含测试策略和部署指南

### 下一步

创建详细的实施计划，分阶段完成开发、测试和部署工作。