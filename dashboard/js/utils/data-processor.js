// dashboard/js/utils/data-processor.js

/**
 * 数据处理器
 * 提供数据筛选、排序、聚合和转换功能
 */
class DataProcessor {
    /**
     * 筛选数据
     * @param {Array} data - 原始数据
     * @param {Object} filters - 筛选条件
     * @returns {Array} 筛选后的数据
     */
    static filterData(data, filters) {
        if (!Array.isArray(data)) return [];
        if (!filters) return data;

        return data.filter(item => {
            // 类型筛选
            if (filters.types && filters.types.length > 0) {
                if (!filters.types.includes(item.type)) {
                    return false;
                }
            }

            // 优先级筛选
            if (filters.priority) {
                const itemPriority = this.getPriority(item.debt_score);
                if (itemPriority !== filters.priority) {
                    return false;
                }
            }

            // 文件路径搜索
            if (filters.filePath && filters.filePath.trim() !== '') {
                if (!item.file_path.toLowerCase().includes(filters.filePath.toLowerCase())) {
                    return false;
                }
            }

            // 复杂度范围筛选
            if (filters.complexityRange) {
                const [min, max] = filters.complexityRange;
                if (item.complexity < min || item.complexity > max) {
                    return false;
                }
            }

            return true;
        });
    }

    /**
     * 排序数据
     * @param {Array} data - 数据数组
     * @param {string} column - 排序列
     * @param {string} order - 排序顺序 ('asc' | 'desc')
     * @returns {Array} 排序后的数据
     */
    static sortData(data, column, order = 'desc') {
        if (!Array.isArray(data)) return [];

        const sorted = [...data].sort((a, b) => {
            let aVal = a[column];
            let bVal = b[column];

            // 处理字符串比较
            if (typeof aVal === 'string' && typeof bVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }

            if (order === 'asc') {
                return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            } else {
                return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
            }
        });

        return sorted;
    }

    /**
     * 聚合统计数据
     * @param {Array} data - 数据数组
     * @returns {Object} 统计数据
     */
    static aggregateStats(data) {
        if (!Array.isArray(data) || data.length === 0) {
            return {
                totalItems: 0,
                highPriority: 0,
                mediumPriority: 0,
                lowPriority: 0,
                avgComplexity: 0,
                totalModifications: 0
            };
        }

        const totalItems = data.length;
        let highPriority = 0;
        let mediumPriority = 0;
        let lowPriority = 0;
        let totalComplexity = 0;
        let totalModifications = 0;

        data.forEach(item => {
            const priority = this.getPriority(item.debt_score);
            if (priority === 'high') highPriority++;
            else if (priority === 'medium') mediumPriority++;
            else lowPriority++;

            totalComplexity += item.complexity || 0;
            totalModifications += item.modification_frequency || 0;
        });

        return {
            totalItems,
            highPriority,
            mediumPriority,
            lowPriority,
            avgComplexity: (totalComplexity / totalItems).toFixed(1),
            totalModifications
        };
    }

    /**
     * 获取优先级
     * @param {number} debtScore - 债务指数
     * @returns {string} 优先级 ('high' | 'medium' | 'low')
     */
    static getPriority(debtScore) {
        if (debtScore >= 0.5) return 'high';
        if (debtScore >= 0.3) return 'medium';
        return 'low';
    }

    /**
     * 转换为饼图数据
     * @param {Array} data - 数据数组
     * @returns {Array} 饼图数据
     */
    static transformForPieChart(data) {
        const typeCounts = {};

        data.forEach(item => {
            const type = item.type || 'unknown';
            typeCounts[type] = (typeCounts[type] || 0) + 1;
        });

        return Object.entries(typeCounts).map(([name, value]) => ({
            name,
            value
        }));
    }

    /**
     * 转换为折线图数据
     * @param {Array} data - 数据数组
     * @param {number} topN - 取前N个
     * @returns {Object} 折线图数据
     */
    static transformForLineChart(data, topN = 10) {
        const sorted = this.sortData(data, 'complexity', 'desc');
        const topItems = sorted.slice(0, topN);

        return {
            labels: topItems.map(item => this.truncateText(item.entity_name, 20)),
            values: topItems.map(item => item.complexity || 0),
            items: topItems
        };
    }

    /**
     * 转换为树图数据
     * @param {Array} data - 数据数组
     * @returns {Array} 树图数据
     */
    static transformForTreeMap(data) {
        const treeData = [];

        // 按文件路径分组
        const fileMap = {};
        data.forEach(item => {
            const filePath = item.file_path;
            if (!fileMap[filePath]) {
                fileMap[filePath] = {
                    name: this.getFileName(filePath),
                    value: 0,
                    item: item
                };
            }
            fileMap[filePath].value += item.complexity || 0;
        });

        // 转换为数组
        Object.values(fileMap).forEach(fileData => {
            treeData.push(fileData);
        });

        return treeData;
    }

    /**
     * 转换为桑基图数据
     * @param {Array} data - 数据数组
     * @returns {Object} 桑基图数据 {nodes, links}
     */
    static transformForSankey(data) {
        const nodes = [];
        const links = [];
        const nodeMap = new Map();

        // 收集节点
        const files = new Set();
        const types = new Set();

        data.forEach(item => {
            files.add(this.getFileName(item.file_path));
            types.add(item.type);
        });

        // 添加文件节点
        files.forEach(file => {
            const nodeId = `file_${file}`;
            nodeMap.set(nodeId, nodes.length);
            nodes.push({
                name: file,
                category: 0
            });
        });

        // 添加类型节点
        types.forEach(type => {
            const nodeId = `type_${type}`;
            nodeMap.set(nodeId, nodes.length);
            nodes.push({
                name: type,
                category: 1
            });
        });

        // 构建链接
        const linkCounts = {};
        data.forEach(item => {
            const file = this.getFileName(item.file_path);
            const type = item.type;
            const key = `${file}__${type}`;

            if (!linkCounts[key]) {
                linkCounts[key] = {
                    source: nodeMap.get(`file_${file}`),
                    target: nodeMap.get(`type_${type}`),
                    value: 0
                };
            }
            linkCounts[key].value += 1;
        });

        Object.values(linkCounts).forEach(link => {
            links.push(link);
        });

        return { nodes, links };
    }

    /**
     * 分页数据
     * @param {Array} data - 数据数组
     * @param {number} page - 页码
     * @param {number} pageSize - 每页大小
     * @returns {Object} 分页结果
     */
    static paginate(data, page = 1, pageSize = 20) {
        const totalItems = data.length;
        const totalPages = Math.ceil(totalItems / pageSize);
        const currentPage = Math.min(Math.max(1, page), totalPages);
        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = Math.min(startIndex + pageSize, totalItems);

        return {
            data: data.slice(startIndex, endIndex),
            pagination: {
                currentPage,
                totalPages,
                pageSize,
                totalItems,
                startIndex: startIndex + 1,
                endIndex
            }
        };
    }

    /**
     * 获取文件名
     * @param {string} filePath - 文件路径
     * @returns {string} 文件名
     */
    static getFileName(filePath) {
        const parts = filePath.split('/');
        return parts[parts.length - 1];
    }

    /**
     * 截断文本
     * @param {string} text - 文本
     * @param {number} maxLength - 最大长度
     * @returns {string} 截断后的文本
     */
    static truncateText(text, maxLength = 50) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// 导出到全局
window.DataProcessor = DataProcessor;
