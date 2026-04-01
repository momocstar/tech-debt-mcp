# tools/sonarqube.py
import os
import requests
from typing import Optional, Dict, List
from models import DebtItem, DebtType

class SonarQubeClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    def get_metrics(self, project_key: str, metrics: List[str]) -> Optional[Dict]:
        """获取项目度量指标"""
        params = {
            'project': project_key,
            'metricKeys': ','.join(metrics)
        }
        resp = self.session.get(f"{self.base_url}/api/measures/component", params=params)
        if resp.status_code == 200:
            data = resp.json()
            measures = data.get('component', {}).get('measures', [])
            return {m['metric']: m['value'] for m in measures}
        return None

    def get_issues(self, project_key: str, types: List[str] = None, severities: List[str] = None, ps: int = 100) -> List[Dict]:
        """获取代码问题（技术债务）"""
        params = {
            'projectKeys': project_key,
            'ps': ps,
            'resolved': 'false'
        }
        if types:
            params['types'] = ','.join(types)
        if severities:
            params['severities'] = ','.join(severities)
        resp = self.session.get(f"{self.base_url}/api/issues/search", params=params)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('issues', [])
        return []

def get_sonarqube_metrics(project_key: str, base_url: str = None, token: str = None) -> dict:
    """
    从 SonarQube 获取度量数据，并转换为 DebtItem 列表。
    base_url 和 token 可以从环境变量读取。
    """
    if not base_url:
        base_url = os.environ.get('SONARQUBE_URL')
    if not token:
        token = os.environ.get('SONARQUBE_TOKEN')
    if not base_url or not token:
        return {"error": "SonarQube URL or token not configured", "items": []}

    client = SonarQubeClient(base_url, token)
    issues = client.get_issues(project_key, types=['CODE_SMELL', 'BUG'], severities=['MAJOR', 'CRITICAL', 'BLOCKER'])

    items = []
    for issue in issues:
        file_path = issue.get('component', '').replace(project_key + ':', '')
        if not file_path:
            continue
        # 根据规则类型映射到 DebtType
        rule = issue.get('rule', '')
        debt_type = DebtType.COMPLEX_METHOD  # 默认
        if 'complexity' in rule.lower():
            debt_type = DebtType.COMPLEX_METHOD
        elif 'duplicate' in rule.lower():
            debt_type = DebtType.DUPLICATE_CODE
        elif 'long' in rule.lower():
            debt_type = DebtType.LONG_METHOD
        elif 'god' in rule.lower() or 'class' in rule.lower():
            debt_type = DebtType.GOD_CLASS
        elif 'coverage' in rule.lower() or 'test' in rule.lower():
            debt_type = DebtType.LOW_COVERAGE

        items.append(DebtItem(
            id=f"{file_path}:{issue.get('line', '')}",
            type=debt_type,
            file_path=file_path,
            entity_name=issue.get('message', '')[:50],
            complexity=issue.get('effort', None),  # 可能无直接复杂度
            custom_notes=issue.get('message', '')
        ))

    return {
        "items": [item.__dict__ for item in items],
        "total_count": len(items),
        "source": "sonarqube"
    }