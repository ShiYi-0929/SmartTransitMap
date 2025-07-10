# 后端环境部署指南

> 适用于 Windows 10/11，Python 3.11（其他 3.8+ 版本通常也可）。

## 1. 克隆代码
```bash
# HTTPS
$ git clone <repo-url> face && cd face
```

## 2. 创建并激活虚拟环境（推荐）
```bash
# Windows CMD
> python -m venv backend\venv
> backend\venv\Scripts\activate

# PowerShell
PS> python -m venv backend/venv
PS> backend/venv/Scripts/Activate.ps1
```

## 3. 安装依赖包
```
(venv) > pip install --upgrade pip
(venv) > pip install -r backend/requirements.txt
```

### 3.1 dlib 安装说明
`face_recognition` 依赖 **dlib**。已在仓库 `Dlib_face_recognition_from_camera-master/` 目录下附带 Windows 预编译轮子：
```
(venv) > pip install Dlib_face_recognition_from_camera-master\dlib-19.24.1-cp311-cp311-win_amd64.whl
```
若使用其他 Python 版本或 Linux/Mac，请确保：
1. 系统已安装 CMake ≥ 3.18
2. C++ 编译器（Windows 推荐 *Build Tools for Visual Studio 2022*，Linux 安装 `build-essential`）
3. 运行 `pip install dlib==19.24.1` 进行源码编译

## 4. 下载人脸模型文件
本仓库已附带所需的 `shape_predictor_68_face_landmarks.dat` 和 `dlib_face_recognition_resnet_model_v1.dat`，位于 `Dlib_face_recognition_from_camera-master/data/data_dlib`。
若缺失，可从以下地址下载并放入同一路径：
- http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
- http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2

## 5. 运行后端
```bash
(venv) > uvicorn backend.app:app --reload --port 8000
```

启动成功后，API 根路径为 `http://localhost:8000`。核心接口：
- `POST /register` 录入人脸
- `POST /verify`   验证人脸
- `GET  /faces`    查询已录入用户
- `DELETE /faces/{person_id}` 删除用户（含图片）
- `DELETE /faces/{person_id}/images/{filename}` 删除指定图片
- `POST /check_face_in_frame` 检测人脸是否在拍摄框内

## 6. 常见问题
| 问题 | 解决方案 |
| ---- | -------- |
| `dlib` 编译失败 / 找不到 CMake | 确认已安装 CMake 并加入环境变量；或使用预编译轮子 |
| `RuntimeError: Unable to open shape_predictor_68_face_landmarks.dat` | 模型文件路径错误，确认文件存在于工作目录 |
| 端口被占用 | 修改 `uvicorn` 命令中的 `--port` 参数 |

## 7. 生产环境部署建议
- 使用 `gunicorn` + `uvicorn.workers.UvicornWorker` 配合 `nginx` 做反向代理；
- 开启 HTTPS；
- 将 `--reload` 替换成 `--workers <n>` 并移除自动热重载。

---
如有疑问，欢迎在项目 Issue 区提问。 