// dashboard/js/components/export-panel.js

/**
 * 导出面板组件
 */
class ExportPanel {
    constructor(containerId, getExportData) {
        this.container = document.getElementById(containerId);
        this.getExportData = getExportData;
        this.active = false;

        this.init();
    }

    /**
     * 初始化
     */
    init() {
        this.bindEvents();
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 关闭按钮
        const closeBtn = this.container.querySelector('#close-export');
        closeBtn.addEventListener('click', () => {
            this.hide();
        });

        // 确认导出按钮
        const confirmBtn = this.container.querySelector('#confirm-export');
        confirmBtn.addEventListener('click', () => {
            this.handleExport();
        });
    }

    /**
     * 显示面板
     */
    show() {
        this.active = true;
        this.container.classList.add('active');
    }

    /**
     * 隐藏面板
     */
    hide() {
        this.active = false;
        this.container.classList.remove('active');
    }

    /**
     * 切换显示状态
     */
    toggle() {
        if (this.active) {
            this.hide();
        } else {
            this.show();
        }
    }

    /**
     * 处理导出
     */
    async handleExport() {
        const format = this.container.querySelector('#export-format').value;
        const scope = this.container.querySelector('#export-scope').value;

        const progressBar = this.container.querySelector('#export-progress');
        const confirmBtn = this.container.querySelector('#confirm-export');

        try {
            // 显示进度条
            progressBar.style.display = 'block';
            confirmBtn.disabled = true;

            // 获取数据
            const data = this.getExportData(scope);

            // 模拟进度
            this.updateProgress(0);
            await this.delay(200);
            this.updateProgress(30);

            // 执行导出
            switch (format) {
                case 'png':
                    await this.exportChartsAsPNG();
                    break;
                case 'excel':
                    await ExportUtils.exportDataAsExcel(data, 'tech-debt.xlsx');
                    break;
                case 'pdf':
                    const stats = DataProcessor.aggregateStats(data);
                    await ExportUtils.exportAsPDF(data, stats, 'tech-debt-report.pdf');
                    break;
            }

            this.updateProgress(100);
            await this.delay(500);

            showToast('导出成功', 'success');
            this.hide();

        } catch (error) {
            showToast(`导出失败: ${error.message}`, 'error');
        } finally {
            progressBar.style.display = 'none';
            confirmBtn.disabled = false;
            this.updateProgress(0);
        }
    }

    /**
     * 导出图表为PNG
     */
    async exportChartsAsPNG() {
        if (!window.app || !window.app.chartManager) {
            throw new Error('图表未初始化');
        }

        const charts = window.app.chartManager.charts;
        await ExportUtils.exportAllChartsAsPNG(charts);
    }

    /**
     * 更新进度条
     */
    updateProgress(percent) {
        const progressBar = this.container.querySelector('#export-progress .bar');
        progressBar.style.width = `${percent}%`;
    }

    /**
     * 延迟函数
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 导出到全局
window.ExportPanel = ExportPanel;
