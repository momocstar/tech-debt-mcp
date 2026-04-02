// dashboard/js/components/detail-modal.js

/**
 * 详情模态框组件
 */
class DetailModal {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentItem = null;

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
        const closeBtn = this.container.querySelector('#close-modal');
        closeBtn.addEventListener('click', () => {
            this.hide();
        });

        // 遮罩层点击关闭
        const overlay = this.container.querySelector('.modal-overlay');
        overlay.addEventListener('click', () => {
            this.hide();
        });

        // 导出按钮
        const exportBtn = this.container.querySelector('#export-item');
        exportBtn.addEventListener('click', () => {
            this.exportItem();
        });

        // 标记已处理按钮
        const markBtn = this.container.querySelector('#mark-processed');
        markBtn.addEventListener('click', () => {
            this.markProcessed();
        });

        // ESC键关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.container.classList.contains('active')) {
                this.hide();
            }
        });
    }

    /**
     * 显示详情
     */
    show(item) {
        this.currentItem = item;
        this.render();
        this.container.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    /**
     * 隐藏详情
     */
    hide() {
        this.container.classList.remove('active');
        document.body.style.overflow = '';
        this.currentItem = null;
    }

    /**
     * 渲染详情内容
     */
    render() {
        const modalBody = this.container.querySelector('#modal-body');
        const item = this.currentItem;

        if (!item) {
            modalBody.innerHTML = '<p>无数据</p>';
            return;
        }

        const priority = DataProcessor.getPriority(item.debt_score);
        const priorityText = priority === 'high' ? '高' : priority === 'medium' ? '中' : '低';

        modalBody.innerHTML = `
            <div class="detail-section">
                <h5>基本信息</h5>
                <table class="table">
                    <tbody>
                        <tr>
                            <td style="width: 30%;"><strong>类型</strong></td>
                            <td>${item.type}</td>
                        </tr>
                        <tr>
                            <td><strong>文件路径</strong></td>
                            <td>${item.file_path}</td>
                        </tr>
                        <tr>
                            <td><strong>实体名称</strong></td>
                            <td>${item.entity_name}</td>
                        </tr>
                        <tr>
                            <td><strong>复杂度</strong></td>
                            <td>${item.complexity}</td>
                        </tr>
                        <tr>
                            <td><strong>债务指数</strong></td>
                            <td>${item.debt_score.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <td><strong>优先级</strong></td>
                            <td class="priority-${priority}">${priorityText}</td>
                        </tr>
                        <tr>
                            <td><strong>修改频率</strong></td>
                            <td>${item.modification_frequency || 0}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            ${item.ai_suggestion ? `
                <div class="detail-section" style="margin-top: 20px;">
                    <h5>AI重构建议</h5>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px;">
                        ${item.ai_suggestion}
                    </div>
                </div>
            ` : ''}

            <div class="detail-section" style="margin-top: 20px;">
                <h5>位置信息</h5>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px;">
                    <p><strong>文件:</strong> ${item.file_path}</p>
                    ${item.start_line ? `<p><strong>起始行:</strong> ${item.start_line}</p>` : ''}
                    ${item.end_line ? `<p><strong>结束行:</strong> ${item.end_line}</p>` : ''}
                </div>
            </div>
        `;
    }

    /**
     * 导出当前项
     */
    async exportItem() {
        if (!this.currentItem) {
            alert('没有可导出的数据');
            return;
        }

        try {
            await ExportUtils.exportDataAsExcel([this.currentItem], `tech-debt-${this.currentItem.entity_name}.xlsx`);
            showToast('导出成功', 'success');
        } catch (error) {
            showToast(`导出失败: ${error.message}`, 'error');
        }
    }

    /**
     * 标记已处理
     */
    markProcessed() {
        if (!this.currentItem) return;

        // 这里可以实现标记逻辑，比如保存到本地存储或发送到后端
        console.log('标记已处理:', this.currentItem);

        showToast('已标记为处理状态', 'success');
        this.hide();
    }
}

/**
 * 显示Toast通知
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <button class="btn btn-clear float-right" onclick="this.parentElement.remove()"></button>
        <p>${message}</p>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// 导出到全局
window.DetailModal = DetailModal;
window.showToast = showToast;
