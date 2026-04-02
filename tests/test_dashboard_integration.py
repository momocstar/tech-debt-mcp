# tests/test_dashboard_integration.py
import os
import json
import tempfile
import shutil
from pathlib import Path
from dashboard import DashboardGenerator


class TestDashboardIntegration:
    """仪表盘集成测试"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_path = os.path.join(self.temp_dir, 'dashboard.html')

        self.sample_data = {
            "items": [
                {
                    'type': 'complex_method',
                    'file_path': '/path/to/File1.java',
                    'entity_name': 'ComplexMethod',
                    'complexity': 25,
                    'debt_score': 0.85,
                    'modification_frequency': 10
                },
                {
                    'type': 'long_method',
                    'file_path': '/path/to/File2.py',
                    'entity_name': 'LongMethod',
                    'complexity': 15,
                    'debt_score': 0.72,
                    'modification_frequency': 8
                },
                {
                    'type': 'god_class',
                    'file_path': '/path/to/File3.java',
                    'entity_name': 'GodClass',
                    'complexity': 30,
                    'debt_score': 0.92,
                    'modification_frequency': 15
                }
            ]
        }

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_generate_html_report_creates_files(self):
        """测试HTML报告生成创建文件"""
        DashboardGenerator.generate_html_report(
            self.sample_data,
            self.output_path,
            "测试报告"
        )

        # 验证HTML文件已创建
        assert os.path.exists(self.output_path)

        # 验证dashboard目录已复制
        dashboard_dir = os.path.join(self.temp_dir, 'dashboard')
        assert os.path.exists(dashboard_dir)

    def test_html_contains_data(self):
        """测试HTML包含数据"""
        DashboardGenerator.generate_html_report(
            self.sample_data,
            self.output_path,
            "测试报告"
        )

        # 读取HTML内容
        with open(self.output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 验证数据已注入
        assert 'window.dashboardData' in html_content
        assert 'ComplexMethod' in html_content
        assert 'LongMethod' in html_content

    def test_html_contains_title(self):
        """测试HTML包含正确的标题"""
        title = "自定义测试报告"
        DashboardGenerator.generate_html_report(
            self.sample_data,
            self.output_path,
            title
        )

        # 读取HTML内容
        with open(self.output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 验证标题
        assert title in html_content

    def test_dashboard_directory_structure(self):
        """测试dashboard目录结构"""
        DashboardGenerator.generate_html_report(
            self.sample_data,
            self.output_path,
            "测试报告"
        )

        dashboard_dir = os.path.join(self.temp_dir, 'dashboard')

        # 验证必要的文件和目录存在
        assert os.path.exists(os.path.join(dashboard_dir, 'index.html'))
        assert os.path.exists(os.path.join(dashboard_dir, 'css'))
        assert os.path.exists(os.path.join(dashboard_dir, 'js'))

    def test_javascript_files_exist(self):
        """测试JavaScript文件存在"""
        DashboardGenerator.generate_html_report(
            self.sample_data,
            self.output_path,
            "测试报告"
        )

        dashboard_dir = os.path.join(self.temp_dir, 'dashboard')

        # 验证JavaScript文件
        js_files = [
            'js/app.js',
            'js/utils/data-processor.js',
            'js/utils/export-utils.js',
            'js/charts/chart-manager.js',
            'js/components/filter-panel.js',
            'js/components/data-table.js',
            'js/components/detail-modal.js',
            'js/components/export-panel.js'
        ]

        for js_file in js_files:
            path = os.path.join(dashboard_dir, js_file)
            assert os.path.exists(path), f"文件不存在: {js_file}"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
