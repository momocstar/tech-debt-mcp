// dashboard/js/components/data-table.js

/**
 * 数据表格组件
 */
class DataTable {
    constructor(containerId, onRowClick, onSelectionChange) {
        this.container = document.getElementById(containerId);
        this.onRowClick = onRowClick;
        this.onSelectionChange = onSelectionChange;
        this.data = [];
        this.displayData = [];
        this.currentPage = 1;
        this.pageSize = 20;
        this.sortColumn = 'debt_score';
        this.sortOrder = 'desc';
        this.selectedRows = new Set();

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
        // 全选复选框
        const selectAllCheckbox = this.container.querySelector('#select-all');
        selectAllCheckbox.addEventListener('change', (e) => {
            this.toggleSelectAll(e.target.checked);
        });

        // 表头排序
        const headers = this.container.querySelectorAll('thead th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const column = header.dataset.sortable;
                this.sort(column);
            });
        });

        // 展开全部按钮
        const expandAllBtn = this.container.querySelector('#expand-all');
        expandAllBtn.addEventListener('click', () => {
            this.toggleExpandAll();
        });
    }

    /**
     * 更新数据
     */
    updateData(data) {
        this.data = data;
        this.currentPage = 1;
        this.selectedRows.clear();
        this.render();
    }

    /**
     * 渲染表格
     */
    render() {
        // 排序
        this.displayData = DataProcessor.sortData(this.data, this.sortColumn, this.sortOrder);

        // 分页
        const { data: pageData, pagination } = DataProcessor.paginate(
            this.displayData,
            this.currentPage,
            this.pageSize
        );

        // 渲染表格主体
        this.renderTableBody(pageData);

        // 渲染分页
        this.renderPagination(pagination);

        // 更新全选复选框状态
        this.updateSelectAllCheckbox();
    }

    /**
     * 渲染表格主体
     */
    renderTableBody(data) {
        const tbody = this.container.querySelector('#data-table-body');

        if (data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align: center; padding: 40px;">
                        <div class="empty">
                            <p class="empty-title h5">暂无数据</p>
                            <p class="empty-subtitle">请调整筛选条件</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.map((item, index) => {
            const priority = DataProcessor.getPriority(item.debt_score);
            const priorityText = priority === 'high' ? '高' : priority === 'medium' ? '中' : '低';
            const globalIndex = (this.currentPage - 1) * this.pageSize + index;

            return `
                <tr data-index="${globalIndex}" data-id="${item.file_path}-${item.entity_name}">
                    <td>
                        <input type="checkbox" class="row-checkbox" data-index="${globalIndex}">
                    </td>
                    <td>${globalIndex + 1}</td>
                    <td>${item.type}</td>
                    <td title="${item.file_path}">${DataProcessor.truncateText(item.file_path, 30)}</td>
                    <td>${DataProcessor.truncateText(item.entity_name, 25)}</td>
                    <td>${item.complexity}</td>
                    <td>${item.debt_score.toFixed(2)}</td>
                    <td class="priority-${priority}">${priorityText}</td>
                    <td>
                        <button class="btn btn-sm btn-action" onclick="app.showDetail('${globalIndex}')">
                            <i class="icon icon-more-horiz"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        // 绑定行点击事件
        tbody.querySelectorAll('tr[data-index]').forEach(row => {
            row.addEventListener('click', (e) => {
                // 避免复选框点击触发行点击
                if (e.target.type === 'checkbox' || e.target.closest('button')) {
                    return;
                }
                const index = parseInt(row.dataset.index);
                this.handleRowClick(index);
            });

            // 绑定复选框事件
            const checkbox = row.querySelector('.row-checkbox');
            checkbox.addEventListener('change', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.toggleRowSelection(index, e.target.checked);
            });
        });
    }

    /**
     * 渲染分页
     */
    renderPagination(pagination) {
        const paginationContainer = this.container.querySelector('#pagination');

        const { currentPage, totalPages, totalItems, startIndex, endIndex } = pagination;

        let html = `
            <button class="btn btn-sm" ${currentPage === 1 ? 'disabled' : ''} onclick="app.changePage(${currentPage - 1})">
                上一页
            </button>
        `;

        // 页码按钮
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <button class="btn btn-sm ${i === currentPage ? 'btn-primary' : ''}" onclick="app.changePage(${i})">
                    ${i}
                </button>
            `;
        }

        html += `
            <button class="btn btn-sm" ${currentPage === totalPages ? 'disabled' : ''} onclick="app.changePage(${currentPage + 1})">
                下一页
            </button>
            <span class="pagination-info">
                显示 ${startIndex}-${endIndex} / 共 ${totalItems} 条
            </span>
        `;

        paginationContainer.innerHTML = html;
    }

    /**
     * 排序
     */
    sort(column) {
        if (this.sortColumn === column) {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortOrder = 'desc';
        }

        this.render();
    }

    /**
     * 切换页码
     */
    changePage(page) {
        this.currentPage = page;
        this.render();
    }

    /**
     * 处理行点击
     */
    handleRowClick(index) {
        if (this.onRowClick) {
            this.onRowClick(this.displayData[index]);
        }
    }

    /**
     * 切换全选
     */
    toggleSelectAll(checked) {
        const checkboxes = this.container.querySelectorAll('.row-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            const index = parseInt(checkbox.dataset.index);
            if (checked) {
                this.selectedRows.add(index);
            } else {
                this.selectedRows.delete(index);
            }
        });

        if (this.onSelectionChange) {
            this.onSelectionChange(Array.from(this.selectedRows));
        }
    }

    /**
     * 切换行选择
     */
    toggleRowSelection(index, selected) {
        if (selected) {
            this.selectedRows.add(index);
        } else {
            this.selectedRows.delete(index);
        }

        this.updateSelectAllCheckbox();

        if (this.onSelectionChange) {
            this.onSelectionChange(Array.from(this.selectedRows));
        }
    }

    /**
     * 更新全选复选框状态
     */
    updateSelectAllCheckbox() {
        const selectAllCheckbox = this.container.querySelector('#select-all');
        const checkboxes = this.container.querySelectorAll('.row-checkbox');
        const checkedCount = this.selectedRows.size;

        if (checkedCount === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checkedCount === checkboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }

    /**
     * 切换展开全部
     */
    toggleExpandAll() {
        // 实现展开全部详情的逻辑（可选）
        console.log('展开全部详情');
    }

    /**
     * 获取选中的数据
     */
    getSelectedData() {
        return Array.from(this.selectedRows).map(index => this.displayData[index]);
    }
}

// 导出到全局
window.DataTable = DataTable;
