// dashboard/js/app.js

/**
 * 主应用类
 */
class DashboardApp {
    constructor() {
        this.state = {
            rawData: [],
            filteredData: [],
            filters: {},
            stats: {}
        };

        this.components = {
            filterPanel: null,
            dataTable: null,
            detailModal: null,
            exportPanel: null,
            chartManager: null
        };

        this.init();
    }

    /**
     * 初始化应用
     */
    async init() {
        try {
            // 加载数据
            await this.loadData();

            // 初始化组件
            this.initComponents();

            // 首次渲染
            this.render();

            console.log('仪表盘应用初始化成功');
        } catch (error) {
            console.error('仪表盘应用初始化失败:', error);
            this.showError('应用初始化失败', error.message);
        }
    }

    /**
     * 加载数据
     */
    async loadData() {
        // 从window.dashboardData获取Python注入的数据
        if (!window.dashboardData || !Array.isArray(window.dashboardData)) {
            throw new Error('数据格式不正确或数据不存在');
        }

        this.state.rawData = window.dashboardData;
        this.state.filteredData = window.dashboardData;

        console.log(`成功加载 ${this.state.rawData.length} 条数据`);
    }

    /**
     * 初始化组件
     */
    initComponents() {
        // 初始化筛选面板
        this.components.filterPanel = new FilterPanel(
            'filter-panel',
            this.handleFilterChange.bind(this)
        );

        // 初始化数据表格
        this.components.dataTable = new DataTable(
            'data-table-container',
            this.handleRowClick.bind(this),
            this.handleSelectionChange.bind(this)
        );

        // 初始化详情模态框
        this.components.detailModal = new DetailModal('detail-modal');

        // 初始化导出面板
        this.components.exportPanel = new ExportPanel(
            'export-panel',
            this.getExportData.bind(this)
        );

        // 初始化图表管理器
        this.components.chartManager = new ChartManager();

        // 绑定全局事件
        this.bindGlobalEvents();
    }

    /**
     * 绑定全局事件
     */
    bindGlobalEvents() {
        // 导出按钮
        const exportBtn = document.getElementById('export-btn');
        exportBtn.addEventListener('click', () => {
            this.components.exportPanel.toggle();
        });

        // 刷新按钮
        const refreshBtn = document.getElementById('refresh-btn');
        refreshBtn.addEventListener('click', () => {
            this.refresh();
        });
    }

    /**
     * 渲染
     */
    render() {
        // 计算统计数据
        this.state.stats = DataProcessor.aggregateStats(this.state.filteredData);

        // 更新统计卡片
        this.updateStatsCards();

        // 更新图表
        this.components.chartManager.updateCharts(this.state.filteredData);

        // 更新数据表格
        this.components.dataTable.updateData(this.state.filteredData);
    }

    /**
     * 更新统计卡片
     */
    updateStatsCards() {
        const statsGrid = document.getElementById('stats-grid');
        const stats = this.state.stats;

        statsGrid.innerHTML = `
            <div class="stat-card">
                <h3>总债务项</h3>
                <p>${stats.totalItems}</p>
            </div>

            <div class="stat-card high-priority">
                <h3>高优先级</h3>
                <p>${stats.highPriority}</p>
            </div>

            <div class="stat-card">
                <h3>平均复杂度</h3>
                <p>${stats.avgComplexity}</p>
            </div>

            <div class="stat-card">
                <h3>总修改次数</h3>
                <p>${stats.totalModifications}</p>
            </div>
        `;
    }

    /**
     * 处理筛选条件变化
     */
    handleFilterChange(filters) {
        this.state.filters = filters;

        // 应用筛选
        this.state.filteredData = DataProcessor.filterData(this.state.rawData, filters);

        // 重新渲染
        this.render();

        console.log(`筛选后剩余 ${this.state.filteredData.length} 条数据`);
    }

    /**
     * 处理表格行点击
     */
    handleRowClick(item) {
        this.components.detailModal.show(item);
    }

    /**
     * 处理选择变化
     */
    handleSelectionChange(selectedIndices) {
        console.log(`已选择 ${selectedIndices.length} 项`);
    }

    /**
     * 处理图表点击
     */
    handleChartClick(containerId, params) {
        console.log(`图表 ${containerId} 点击:`, params);

        // 可以根据点击的图表类型实现不同的交互
        // 例如：点击饼图的某个扇区，筛选该类型的数据
        if (containerId === 'chart-type' && params.name) {
            this.components.filterPanel.filters.types = [params.name];
            this.components.filterPanel.applyFilter();
        }
    }

    /**
     * 获取导出数据
     */
    getExportData(scope) {
        if (scope === 'filtered') {
            return this.state.filteredData;
        } else {
            return this.state.rawData;
        }
    }

    /**
     * 显示详情（供全局调用）
     */
    showDetail(index) {
        const item = this.state.filteredData[index];
        if (item) {
            this.components.detailModal.show(item);
        }
    }

    /**
     * 切换页码（供全局调用）
     */
    changePage(page) {
        this.components.dataTable.changePage(page);
    }

    /**
     * 刷新数据
     */
    refresh() {
        // 重新加载数据（可以在这里添加从服务器获取新数据的逻辑）
        showToast('正在刷新...', 'info');

        // 重新渲染
        this.render();

        setTimeout(() => {
            showToast('刷新成功', 'success');
        }, 500);
    }

    /**
     * 显示错误
     */
    showError(title, message) {
        const container = document.getElementById('app-container');
        container.innerHTML = `
            <div class="empty">
                <div class="empty-icon">
                    <i class="icon icon-4x icon-stop" style="color: #e74c3c;"></i>
                </div>
                <p class="empty-title h5">${title}</p>
                <p class="empty-subtitle">${message}</p>
                <button class="btn btn-primary" onclick="location.reload()">重新加载</button>
            </div>
        `;
    }
}

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DashboardApp();
});
