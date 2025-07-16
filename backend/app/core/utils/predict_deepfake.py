# 本文件从 QuantumFaceAntiSpoofing-main/predict_deepfake.py 复制而来，保持接口一致

import os
import numpy as np
import torch
from torch import nn
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit_machine_learning.connectors import TorchConnector
from qiskit_machine_learning.neural_networks import EstimatorQNN
from qiskit.primitives import Estimator
from qiskit.quantum_info import Statevector
from PIL import Image
import joblib
import warnings
from tqdm import tqdm

warnings.filterwarnings('ignore')

IMAGE_SIZE = (8, 8)
NUM_QUBITS = 8

def quantum_amplitude_encoding(img_vector, target_qubits=8):
    target_length = 2 ** target_qubits
    if len(img_vector) > target_length:
        img_vector = img_vector[:target_length]
    elif len(img_vector) < target_length:
        padding = np.zeros(target_length - len(img_vector))
        img_vector = np.concatenate([img_vector, padding])
    normalized_vector = img_vector / (np.linalg.norm(img_vector) + 1e-8)
    try:
        state = Statevector(normalized_vector)
        complex_data = state.data.astype(np.complex128)
        phase = np.angle(complex_data)
        phase_normalized = (phase + np.pi) % (2 * np.pi) - np.pi
        encoded = np.abs(complex_data) * np.exp(1j * phase_normalized)
        return encoded
    except Exception:
        return normalized_vector.astype(np.complex128)

def advanced_feature_encoder(X, amplification_factor=3):
    amplitudes = np.abs(X)
    phases = np.angle(X)
    phase_median = np.median(phases, axis=1, keepdims=True)
    phase_std = np.std(phases, axis=1, keepdims=True) + 1e-8
    phases_normalized = (phases - phase_median) / phase_std
    phases_enhanced = np.tanh(phases_normalized * amplification_factor)
    log_amplitudes = np.log1p(amplitudes)
    normalized_amplitudes = amplitudes / (np.max(amplitudes, axis=1, keepdims=True) + 1e-8)
    phase_gradients = np.diff(phases, axis=1, prepend=phases[:, :1])
    amplitude_phase_product = amplitudes * np.cos(phases)
    amplitude_mean = np.mean(amplitudes, axis=1, keepdims=True)
    amplitude_var = np.var(amplitudes, axis=1, keepdims=True)
    phase_coherence = np.abs(np.mean(np.exp(1j * phases), axis=1, keepdims=True))
    features = np.concatenate([
        log_amplitudes,
        normalized_amplitudes,
        phases_enhanced,
        phase_gradients,
        amplitude_phase_product,
        np.tile(amplitude_mean, (1, amplitudes.shape[1])),
        np.tile(amplitude_var, (1, amplitudes.shape[1])),
        np.tile(phase_coherence.real, (1, amplitudes.shape[1])),
    ], axis=1)
    return features

def create_optimized_circuit(num_qubits=8):
    qc = QuantumCircuit(num_qubits)
    x_params = [Parameter(f"x{i}") for i in range(num_qubits)]
    theta_params = [Parameter(f"theta{i}") for i in range(6 * num_qubits)]
    for i in range(num_qubits):
        qc.h(i)
        qc.ry(x_params[i], i)
    param_idx = 0
    for _ in range(3):
        for i in range(num_qubits):
            qc.cx(i, (i + 1) % num_qubits)
        for i in range(num_qubits):
            qc.ry(theta_params[param_idx], i)
            qc.rz(theta_params[param_idx + num_qubits], i)
            param_idx += 1
        param_idx += num_qubits
    return qc

class OptimizedQuantumClassifier(nn.Module):
    def __init__(self, qnn, input_dim, num_qubits):
        super().__init__()
        self.feature_processor = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        self.quantum_adapter = nn.Sequential(
            nn.Linear(128, num_qubits * 2),
            nn.LayerNorm(num_qubits * 2),
            nn.Tanh(),
            nn.Linear(num_qubits * 2, num_qubits),
            nn.LayerNorm(num_qubits),
        )
        self.qnn = TorchConnector(qnn)
        self.post_processor = nn.Sequential(
            nn.Linear(1, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1),
        )
        self.residual_processor = nn.Sequential(
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )
    def forward(self, x):
        processed_features = self.feature_processor(x)
        quantum_input = self.quantum_adapter(processed_features)
        quantum_output = self.qnn(quantum_input)
        quantum_result = self.post_processor(quantum_output)
        classical_result = self.residual_processor(processed_features)
        combined = quantum_result + 0.3 * classical_result
        return torch.sigmoid(combined) 