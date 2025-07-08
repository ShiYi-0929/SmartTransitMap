# detect/inference.py

import random

def predict_disease(file_path: str):
    """
    模拟病害识别结果。
    实际情况中这里会加载模型，对图像进行分析。
    """
    mock_results = [
        {
            "disease_type": random.choice(["龟裂", "坑洼", "横裂", "纵裂"]),
            "position": [random.randint(50, 300), random.randint(50, 300), random.randint(350, 600), random.randint(350, 600)],
            "area": round(random.uniform(20.0, 100.0), 2),
            "severity": random.randint(1, 5)
        }
        for _ in range(random.randint(1, 3))
    ]

    return {
        "status": "success",
        "file": file_path,
        "result": mock_results
    }
