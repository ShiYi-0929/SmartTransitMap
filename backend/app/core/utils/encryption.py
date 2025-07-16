from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

from app.core.config import AES_KEY

# --- AES-GCM 配置 ---
# GCM模式推荐使用12字节的nonce
NONCE_SIZE = 12
# GCM认证标签通常为16字节
TAG_SIZE = 16
# 将配置中的十六进制密钥转换为字节
KEY = bytes.fromhex(AES_KEY)


def encrypt_data(data: bytes) -> bytes:
    """
    使用 AES-GCM 加密数据。

    Args:
        data: 待加密的原始字节数据。

    Returns:
        加密后的字节数据，格式为 (nonce || ciphertext || tag)。
    """
    if not isinstance(data, bytes):
        raise TypeError("加密数据必须是字节类型")

    # 1. 生成一个随机的、不可预测的 nonce (IV)
    nonce = os.urandom(NONCE_SIZE)

    # 2. 创建 AES-GCM Cipher 上下文
    cipher = Cipher(algorithms.AES(KEY), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()

    # 3. 进行加密
    ciphertext = encryptor.update(data) + encryptor.finalize()

    # 4. 将 nonce、密文和认证标签拼接后返回
    # 这样解密时就能从这一个数据块中获取所有必要信息
    return nonce + ciphertext + encryptor.tag


def decrypt_data(encrypted_data: bytes) -> bytes:
    """
    使用 AES-GCM 解密数据。

    Args:
        encrypted_data: 加密后的字节数据 (nonce || ciphertext || tag)。

    Returns:
        解密后的原始字节数据。

    Raises:
        ValueError: 如果数据被篡改或解密失败。
    """
    if not isinstance(encrypted_data, bytes):
        raise TypeError("解密数据必须是字节类型")
    
    if len(encrypted_data) < NONCE_SIZE + TAG_SIZE:
        raise ValueError("无效的加密数据：长度过短")

    # 1. 从加密数据中分离 nonce, ciphertext, 和 tag
    nonce = encrypted_data[:NONCE_SIZE]
    tag = encrypted_data[-TAG_SIZE:]
    ciphertext = encrypted_data[NONCE_SIZE:-TAG_SIZE]

    # 2. 创建 AES-GCM Cipher 上下文
    cipher = Cipher(algorithms.AES(KEY), modes.GCM(nonce, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    # 3. 进行解密和认证
    # `finalize()` 会检查认证标签，如果验证失败会抛出 InvalidTag 异常
    try:
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        return decrypted_data
    except Exception as e:
        # 在实际应用中，这里应该记录一个严重的警告，因为这可能意味着数据被攻击
        raise ValueError(f"解密失败或数据认证失败: {e}") 