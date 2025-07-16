import os
import cv2
import numpy as np
import torch
import joblib
from typing import Tuple, Dict

from .predict_deepfake import (
    advanced_feature_encoder,
    create_optimized_circuit,
    OptimizedQuantumClassifier,
    quantum_amplitude_encoding,
)

from qiskit.primitives import Estimator
from qiskit_machine_learning.neural_networks import EstimatorQNN

# ---------------------------------------------
# 常量与全局缓存
# ---------------------------------------------
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MODELS_DIR = os.path.join(BACKEND_DIR, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "best_optimized_quantum_model_LAB.pth")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler_LAB.pkl")

NUM_QUBITS = 8
PREDICTION_THRESHOLD = 0.165

_model = None  # type: torch.nn.Module | None
_scaler = None  # type: joblib | None

# ---------------------------------------------
# 公共函数
# ---------------------------------------------

def load_model() -> Tuple[torch.nn.Module, joblib]:
    """惰性加载量子模型与特征缩放器，返回 (model, scaler)。"""
    global _model, _scaler
    if _model is not None and _scaler is not None:
        return _model, _scaler

    try:
        _scaler = joblib.load(SCALER_PATH)

        qc = create_optimized_circuit(NUM_QUBITS)
        estimator = Estimator()
        qnn = EstimatorQNN(
            circuit=qc,
            input_params=qc.parameters[:NUM_QUBITS],
            weight_params=qc.parameters[NUM_QUBITS:],
            estimator=estimator,
        )

        _model = OptimizedQuantumClassifier(qnn, 2048, NUM_QUBITS)
        _model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        _model.eval()
        print("[antispoof] ✅ Quantum model & scaler loaded")
    except Exception as e:
        print(f"[antispoof] ❌ Failed to load model or scaler: {e}")
        _model = None
        _scaler = None

    return _model, _scaler


def preprocess_frame_for_prediction(frame: np.ndarray) -> np.ndarray:
    """将 BGR 帧预处理为 256 维特征向量。"""
    from PIL import Image

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)

    img = img_pil.convert("L").resize((8, 8))
    img_array = np.array(img, dtype=np.float32)

    normalized = img_array / 255.0
    flat = normalized.flatten()
    grad_x = np.gradient(normalized, axis=1).flatten()
    grad_y = np.gradient(normalized, axis=0).flatten()
    local_mean = np.mean(normalized)
    local_std = np.std(normalized)
    local_features = np.array([local_mean, local_std])

    combined_features = np.concatenate([
        flat,
        grad_x[:32],
        grad_y[:32],
        np.tile(local_features, 64),
    ])

    if len(combined_features) > 256:
        combined_features = combined_features[:256]
    elif len(combined_features) < 256:
        padding = np.zeros(256 - len(combined_features))
        combined_features = np.concatenate([combined_features, padding])

    return combined_features / (np.linalg.norm(combined_features) + 1e-8)


def predict_single_frame(frame: np.ndarray) -> Dict:
    """返回 {quantum_label, score} 或 {error:msg}"""
    model, scaler = load_model()
    if model is None or scaler is None:
        return {"error": "model_not_loaded"}

    try:
        print("[antispoof] Preprocessing frame for prediction...")
        processed_vector = preprocess_frame_for_prediction(frame)
        print("[antispoof] Encoding quantum state...")
        quantum_state = quantum_amplitude_encoding(processed_vector)
        print("[antispoof] Encoding advanced features...")
        X_feat = advanced_feature_encoder(quantum_state.reshape(1, -1))
        print("[antispoof] Scaling features...")
        X_scaled = scaler.transform(X_feat)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

        print("[antispoof] Running model prediction...")
        with torch.no_grad():
            score = model(X_tensor).item()
            pred = 1 if score > PREDICTION_THRESHOLD else 0
        print(f"[antispoof] Prediction complete. Score: {score}, Label: {'伪造' if pred == 1 else '真实'}")

        return {"quantum_label": "伪造" if pred == 1 else "真实", "score": score}
    except Exception as e:
        print(f"[antispoof] ❌ Error during single frame prediction: {e}")
        return {"error": f"predict_error: {e}"}

# ---------------------------------------------
# 额外检测：光感
# ---------------------------------------------

def light_check(frame: np.ndarray, thresh: float = 50.0) -> bool:
    """简单光感检测：灰度均值大于阈值视为通过。"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(gray))
    return mean_val > thresh 