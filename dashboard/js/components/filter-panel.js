// dashboard/js/components/filter-panel.js

/**
 * 筛选面板组件
 */
class FilterPanel {
    constructor(containerId, onFilterChange) {
        this.container = document.getElementById(containerId);
        this.onFilterChange = onFilterChange;
        this.filters = {
            types: [],
            priority: null,
            filePath: '',
            complexityRange: [0, 100]
        };
        this.collapsed = false;

        this.init();
    }

    /**
     * 初始化
     */
    init() {
        this.render();
        this.bindEvents();
    }

    /**
     * 渲染筛选面板
     */
    render() {
        const filterBody = this.container.querySelector('#filter-body');

        filterBody.innerHTML = `
            <div class="filter-row">
                <div class="filter-group">
                    <label>债务类型</label>
                    <select class="form-select" id="filter-types" multiple>
                        <option value="complex_method">复杂方法</option>
                        <option value="long_method">长方法</option>
                        <option value="god_class">上帝类</option>
                        <option value="duplicate_code">重复代码</option>
                        <option value="deep_nesting">深层嵌套</option>
                        <option value="magic_number">魔法数字</option>
                        <option value="long_parameter">长参数列表</option>
                        <option value="data_class">数据类</option>
                        <option value="over_comment">过度注释</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label>优先级</label>
                    <select class="form-select" id="filter-priority">
                        <option value="">全部</option>
                        <option value="high">高</option>
                        <option value="medium">中</option>
                        <option value="low">低</option>
                    </select>
                </div>

                <div class="filter-group">
                    <label>文件路径搜索</label>
                    <input type="text" class="form-input" id="filter-filepath" placeholder="输入文件路径...">
                </div>

                <div class="filter-group">
                    <label>复杂度范围</label>
                    <div style="display: flex; gap: 10px;">
                        <input type="number" class="form-input" id="filter-complexity-min" placeholder="最小值" value="0">
                        <span style="line-height: 32px;">-</span>
                        <input type="number" class="form-input" id="filter-complexity-max" placeholder="最大值" value="100">
                    </div>
                </div>
            </div>

            <div class="filter-row">
                <div class="filter-group" style="flex: 0 0 auto;">
                    <button class="btn btn-primary" id="apply-filter">应用筛选</button>
                </div>
                <div class="filter-group" style="flex: 0 0 auto;">
                    <button class="btn" id="reset-filter">重置</button>
                </div>
            </div>

            <!-- 已选筛选条件 -->
            <div class="filter-tags" id="filter-tags" style="margin-top: 15px;">
                <!-- 筛选标签将在这里显示 -->
            </div>
        `;
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 折叠/展开按钮
        const toggleBtn = this.container.querySelector('#toggle-filter');
        toggleBtn.addEventListener('click', () => this.toggle());

        // 应用筛选按钮
        const applyBtn = this.container.querySelector('#apply-filter');
        applyBtn.addEventListener('click', () => this.applyFilter());

        // 重置按钮
        const resetBtn = this.container.querySelector('#reset-filter');
        resetBtn.addEventListener('click', () => this.resetFilter());

        // 文件路径输入框回车事件
        const filePathInput = this.container.querySelector('#filter-filepath');
        filePathInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilter();
            }
        });

        // 类型选择变化
        const typesSelect = this.container.querySelector('#filter-types');
        typesSelect.addEventListener('change', () => {
            this.updateFilterTags();
        });

        // 优先级选择变化
        const prioritySelect = this.container.querySelector('#filter-priority');
        prioritySelect.addEventListener('change', () => {
            this.updateFilterTags();
        });
    }

    /**
     * 折叠/展开
     */
    toggle() {
        this.collapsed = !this.collapsed;
        if (this.collapsed) {
            this.container.classList.add('collapsed');
        } else {
            this.container.classList.remove('collapsed');
        }
    }

    /**
     * 应用筛选
     */
    applyFilter() {
        // 获取类型选择
        const typesSelect = this.container.querySelector('#filter-types');
        const selectedTypes = Array.from(typesSelect.selectedOptions).map(option => option.value);

        // 获取优先级选择
        const prioritySelect = this.container.querySelector('#filter-priority');
        const priority = prioritySelect.value || null;

        // 获取文件路径
        const filePathInput = this.container.querySelector('#filter-filepath');
        const filePath = filePathInput.value.trim();

        // 获取复杂度范围
        const minComplexity = parseInt(this.container.querySelector('#filter-complexity-min').value) || 0;
        const maxComplexity = parseInt(this.container.querySelector('#filter-complexity-max').value) || 100;

        // 更新筛选条件
        this.filters = {
            types: selectedTypes,
            priority: priority,
            filePath: filePath,
            complexityRange: [minComplexity, maxComplexity]
        };

        // 更新筛选标签
        this.updateFilterTags();

        // 触发筛选变化回调
        if (this.onFilterChange) {
            this.onFilterChange(this.filters);
        }
    }

    /**
     * 重置筛选
     */
    resetFilter() {
        // 重置类型选择
        const typesSelect = this.container.querySelector('#filter-types');
        typesSelect.selectedIndex = -1;

        // 重置优先级
        const prioritySelect = this.container.querySelector('#filter-priority');
        prioritySelect.value = '';

        // 重置文件路径
        const filePathInput = this.container.querySelector('#filter-filepath');
        filePathInput.value = '';

        // 重置复杂度范围
        this.container.querySelector('#filter-complexity-min').value = 0;
        this.container.querySelector('#filter-complexity-max').value = 100;

        // 重置筛选条件
        this.filters = {
            types: [],
            priority: null,
            filePath: '',
            complexityRange: [0, 100]
        };

        // 清空筛选标签
        this.updateFilterTags();

        // 触发筛选变化回调
        if (this.onFilterChange) {
            this.onFilterChange(this.filters);
        }
    }

    /**
     * 更新筛选标签
     */
    updateFilterTags() {
        const tagsContainer = this.container.querySelector('#filter-tags');
        const tags = [];

        // 类型标签
        if (this.filters.types.length > 0) {
            const typesSelect = this.container.querySelector('#filter-types');
            const selectedTypes = Array.from(typesSelect.selectedOptions).map(option => option.text);
            tags.push(`类型: ${selectedTypes.join(', ')}`);
        }

        // 优先级标签
        if (this.filters.priority) {
            const priorityText = this.filters.priority === 'high' ? '高' :
                                this.filters.priority === 'medium' ? '中' : '低';
            tags.push(`优先级: ${priorityText}`);
        }

        // 文件路径标签
        if (this.filters.filePath) {
            tags.push(`文件路径: ${this.filters.filePath}`);
        }

        // 复杂度范围标签
        if (this.filters.complexityRange[0] > 0 || this.filters.complexityRange[1] < 100) {
            tags.push(`复杂度: ${this.filters.complexityRange[0]} - ${this.filters.complexityRange[1]}`);
        }

        // 渲染标签
        if (tags.length > 0) {
            tagsContainer.innerHTML = `
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    ${tags.map(tag => `
                        <span class="chip">${tag}</span>
                    `).join('')}
                </div>
            `;
        } else {
            tagsContainer.innerHTML = '';
        }
    }

    /**
     * 获取当前筛选条件
     */
    getFilters() {
        return { ...this.filters };
    }
}

// 导出到全局
window.FilterPanel = FilterPanel;
