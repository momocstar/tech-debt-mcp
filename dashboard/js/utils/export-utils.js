// dashboard/js/utils/export-utils.js

/**
 * 导出工具
 * 提供PNG、Excel、PDF导出功能
 */
class ExportUtils {
    /**
     * 导出图表为PNG
     * @param {Object} chart - ECharts实例
     * @param {string} fileName - 文件名
     */
    static exportChartAsPNG(chart, fileName = 'chart.png') {
        if (!chart) {
            throw new Error('图表实例不存在');
        }

        const url = chart.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
        });

        const link = document.createElement('a');
        link.download = fileName;
        link.href = url;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * 导出所有图表为PNG
     * @param {Object} charts - 图表实例映射
     */
    static exportAllChartsAsPNG(charts) {
        Object.entries(charts).forEach(([chartId, chart]) => {
            if (chart) {
                this.exportChartAsPNG(chart, `${chartId}.png`);
            }
        });
    }

    /**
     * 导出数据为Excel
     * @param {Array} data - 数据数组
     * @param {string} fileName - 文件名
     */
    static async exportDataAsExcel(data, fileName = 'tech-debt.xlsx') {
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('没有可导出的数据');
        }

        // 动态加载SheetJS库
        await this.loadScript('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js');

        // 准备数据
        const rows = data.map((item, index) => ({
            '序号': index + 1,
            '类型': item.type,
            '文件路径': item.file_path,
            '实体名称': item.entity_name,
            '复杂度': item.complexity,
            '债务指数': item.debt_score,
            '优先级': DataProcessor.getPriority(item.debt_score),
            '修改频率': item.modification_frequency || 0
        }));

        // 创建工作簿
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(rows);

        // 设置列宽
        ws['!cols'] = [
            { wch: 6 },   // 序号
            { wch: 15 },  // 类型
            { wch: 40 },  // 文件路径
            { wch: 25 },  // 实体名称
            { wch: 10 },  // 复杂度
            { wch: 10 },  // 债务指数
            { wch: 8 },   // 优先级
            { wch: 10 }   // 修改频率
        ];

        XLSX.utils.book_append_sheet(wb, ws, '技术债务');

        // 导出文件
        XLSX.writeFile(wb, fileName);
    }

    /**
     * 导出为PDF
     * @param {Array} data - 数据数组
     * @param {Object} stats - 统计数据
     * @param {string} fileName - 文件名
     */
    static async exportAsPDF(data, stats, fileName = 'tech-debt-report.pdf') {
        // 动态加载jsPDF库
        await this.loadScript('https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js');
        await this.loadScript('https://cdn.jsdelivr.net/npm/jspdf-autotable@3.5.31/dist/jspdf.plugin.autotable.min.js');

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // 标题
        doc.setFontSize(20);
        doc.text('技术债务分析报告', 105, 20, { align: 'center' });

        // 日期
        doc.setFontSize(10);
        doc.text(`生成日期: ${new Date().toLocaleDateString('zh-CN')}`, 105, 30, { align: 'center' });

        // 统计摘要
        doc.setFontSize(14);
        doc.text('统计摘要', 14, 45);

        doc.setFontSize(10);
        let yPos = 55;
        doc.text(`总债务项: ${stats.totalItems}`, 14, yPos);
        yPos += 7;
        doc.text(`高优先级: ${stats.highPriority}`, 14, yPos);
        yPos += 7;
        doc.text(`中优先级: ${stats.mediumPriority}`, 14, yPos);
        yPos += 7;
        doc.text(`低优先级: ${stats.lowPriority}`, 14, yPos);
        yPos += 7;
        doc.text(`平均复杂度: ${stats.avgComplexity}`, 14, yPos);
        yPos += 7;
        doc.text(`总修改次数: ${stats.totalModifications}`, 14, yPos);
        yPos += 15;

        // 数据表格
        doc.setFontSize(14);
        doc.text('Top 20 债务项', 14, yPos);
        yPos += 10;

        const tableData = data.slice(0, 20).map((item, index) => [
            index + 1,
            item.type,
            DataProcessor.truncateText(item.file_path, 30),
            DataProcessor.truncateText(item.entity_name, 20),
            item.complexity,
            item.debt_score.toFixed(2),
            DataProcessor.getPriority(item.debt_score)
        ]);

        doc.autoTable({
            startY: yPos,
            head: [['序号', '类型', '文件', '实体', '复杂度', '债务指数', '优先级']],
            body: tableData,
            theme: 'striped',
            headStyles: { fillColor: [87, 100, 198] },
            styles: { fontSize: 8 }
        });

        // 页脚
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.text(
                `第 ${i} 页，共 ${pageCount} 页`,
                doc.internal.pageSize.width / 2,
                doc.internal.pageSize.height - 10,
                { align: 'center' }
            );
        }

        // 保存文件
        doc.save(fileName);
    }

    /**
     * 动态加载脚本
     * @param {string} url - 脚本URL
     * @returns {Promise}
     */
    static loadScript(url) {
        return new Promise((resolve, reject) => {
            // 检查是否已加载
            const scripts = document.getElementsByTagName('script');
            for (let i = 0; i < scripts.length; i++) {
                if (scripts[i].src === url) {
                    resolve();
                    return;
                }
            }

            const script = document.createElement('script');
            script.src = url;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`加载脚本失败: ${url}`));
            document.head.appendChild(script);
        });
    }
}

// 导出到全局
window.ExportUtils = ExportUtils;
