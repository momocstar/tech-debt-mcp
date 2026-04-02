// dashboard/js/charts/chart-manager.js

/**
 * 图表管理器
 * 统一管理所有ECharts实例
 */
class ChartManager {
    constructor() {
        this.charts = {};
        this.resizeTimer = null;

        this.init();
    }

    /**
     * 初始化
     */
    init() {
        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    /**
     * 创建图表
     */
    createChart(containerId, chartType, data) {
        const container = document.querySelector(`#${containerId} .chart-container`);
        if (!container) {
            console.error(`图表容器不存在: ${containerId}`);
            return null;
        }

        // 销毁已存在的图表
        if (this.charts[containerId]) {
            this.charts[containerId].dispose();
        }

        // 创建新图表
        const chart = echarts.init(container);
        const options = this.getChartOptions(chartType, data);

        chart.setOption(options);

        // 绑定点击事件
        chart.on('click', (params) => {
            this.handleChartClick(containerId, params);
        });

        this.charts[containerId] = chart;
        return chart;
    }

    /**
     * 获取图表配置
     */
    getChartOptions(chartType, data) {
        switch (chartType) {
            case 'pie':
                return this.getPieChartOptions(data);
            case 'line':
                return this.getLineChartOptions(data);
            case 'treemap':
                return this.getTreeMapOptions(data);
            case 'sankey':
                return this.getSankeyOptions(data);
            default:
                return {};
        }
    }

    /**
     * 环形图配置
     */
    getPieChartOptions(data) {
        const chartData = DataProcessor.transformForPieChart(data);

        return {
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            legend: {
                orient: 'vertical',
                right: 10,
                top: 'center'
            },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: true,
                    formatter: '{b}: {c}'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 16,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: true
                },
                data: chartData
            }]
        };
    }

    /**
     * 折线图配置
     */
    getLineChartOptions(data) {
        const { labels, values } = DataProcessor.transformForLineChart(data, 10);

        return {
            tooltip: {
                trigger: 'axis'
            },
            xAxis: {
                type: 'category',
                data: labels,
                axisLabel: {
                    rotate: 45,
                    interval: 0
                }
            },
            yAxis: {
                type: 'value',
                name: '复杂度'
            },
            series: [{
                type: 'line',
                smooth: true,
                data: values,
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(54, 162, 235, 0.5)' },
                        { offset: 1, color: 'rgba(54, 162, 235, 0.1)' }
                    ])
                },
                lineStyle: {
                    color: '#36A2EB',
                    width: 2
                },
                itemStyle: {
                    color: '#36A2EB'
                }
            }],
            dataZoom: [{
                type: 'inside',
                start: 0,
                end: 100
            }],
            grid: {
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            }
        };
    }

    /**
     * 树图配置
     */
    getTreeMapOptions(data) {
        const treeData = DataProcessor.transformForTreeMap(data);

        return {
            tooltip: {
                formatter: (params) => {
                    return `${params.name}<br/>复杂度: ${params.value}`;
                }
            },
            series: [{
                type: 'treemap',
                data: treeData,
                roam: false,
                nodeClick: 'link',
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
                },
                levels: [{
                    itemStyle: {
                        borderWidth: 0,
                        borderColor: '#fff',
                        gapWidth: 2
                    }
                }, {
                    itemStyle: {
                        borderWidth: 1,
                        borderColor: '#fff',
                        gapWidth: 1
                    },
                    colorSaturation: [0.4, 0.7]
                }]
            }]
        };
    }

    /**
     * 桑基图配置
     */
    getSankeyOptions(data) {
        const { nodes, links } = DataProcessor.transformForSankey(data);

        return {
            tooltip: {
                trigger: 'item',
                triggerOn: 'mousemove'
            },
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
                    curveness: 0.5,
                    opacity: 0.6
                },
                label: {
                    position: 'right',
                    formatter: '{b}'
                },
                layoutIterations: 32
            }]
        };
    }

    /**
     * 更新所有图表
     */
    updateCharts(data) {
        this.createChart('chart-type', 'pie', data);
        this.createChart('chart-trend', 'line', data);
        this.createChart('chart-heatmap', 'treemap', data);
        this.createChart('chart-sankey', 'sankey', data);
    }

    /**
     * 处理图表点击
     */
    handleChartClick(containerId, params) {
        console.log(`图表 ${containerId} 点击:`, params);

        // 触发全局事件
        if (window.app) {
            window.app.handleChartClick(containerId, params);
        }
    }

    /**
     * 处理窗口大小变化
     */
    handleResize() {
        if (this.resizeTimer) {
            clearTimeout(this.resizeTimer);
        }

        this.resizeTimer = setTimeout(() => {
            Object.values(this.charts).forEach(chart => {
                if (chart) {
                    chart.resize();
                }
            });
        }, 300);
    }

    /**
     * 销毁所有图表
     */
    destroyAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.dispose();
            }
        });
        this.charts = {};
    }

    /**
     * 获取图表实例
     */
    getChart(containerId) {
        return this.charts[containerId];
    }
}

// 导出到全局
window.ChartManager = ChartManager;
