# tools/generate_test_data.py
import json
import random


def generate_large_dataset(count=1000):
    """生成大型测试数据集"""
    types = ['complex_method', 'long_method', 'god_class', 'duplicate_code',
             'deep_nesting', 'magic_number', 'long_parameter', 'data_class']

    items = []
    for i in range(count):
        items.append({
            'type': random.choice(types),
            'file_path': f'/project/src/module{random.randint(1, 50)}/File{random.randint(1, 100)}.java',
            'entity_name': f'method_{i}',
            'complexity': random.randint(5, 50),
            'debt_score': random.uniform(0.1, 0.99),
            'modification_frequency': random.randint(0, 20)
        })

    return {'items': items}


if __name__ == '__main__':
    data = generate_large_dataset(1000)
    with open('test-large-data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"生成 {len(data['items'])} 条测试数据")
