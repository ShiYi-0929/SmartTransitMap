from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch
import os

model = None
processor = None
device = "cuda" if torch.cuda.is_available() else "cpu"
model_loaded = False

def load_deepfake_vit_model():
    """
    加载ViT模型和处理器到内存。
    此函数应在主应用的启动事件中被调用。
    """
    global model, processor, model_loaded
    if model_loaded:
        return

    relative_model_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "deepfake_vit_model")
    model_path = os.path.normpath(os.path.abspath(relative_model_path))

    print(f"开始从本地路径加载ViT Deepfake模型: {model_path}...")
    try:
        model = ViTForImageClassification.from_pretrained(model_path).to(device)
        processor = ViTImageProcessor.from_pretrained(model_path)
        model.eval()
        model_loaded = True
        print("ViT Deepfake模型加载成功！")
    except Exception as e:
        print(f"ViT Deepfake模型加载失败: {e}")
        model = None
        processor = None
        model_loaded = False

def predict_deepfake_vit(image: Image.Image) -> dict:
    """
    接收 PIL Image 对象，进行深度伪造检测并返回结果。
    """
    if not model_loaded or not model or not processor:
        return {"error": "ViT模型尚未加载"}

    try:
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        prediction = model.config.id2label[predicted_class_idx]
        return {"prediction": prediction, "raw_score": logits.softmax(dim=-1).tolist()}
    except Exception as e:
        return {"error": f"ViT模型预测时发生错误: {e}"} 