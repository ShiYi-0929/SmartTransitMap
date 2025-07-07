# SmartTransitMap 智能交通与路面病害检测平台

## 项目简介
本项目为智能交通与路面病害检测平台，包含人脸识别、路面病害检测、交通数据可视化、日志与告警等功能。前后端分离，后端基于 Python FastAPI，前端基于 Vue3 + Element Plus。

---

## 目录结构
```
SmartTransitMap/
├── backend/      # 后端 FastAPI 服务
├── frontend/     # 前端 Vue3 项目
├── README.md     # 项目说明文档
└── ...
```

---

## 一、后端（FastAPI）

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务
```bash
uvicorn main:app --reload
```

### 3. 访问接口文档
- 打开浏览器访问: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 二、前端（Vue3）

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 启动前端开发服务器
```bash
npm run dev
```

### 3. 访问前端页面
- 打开浏览器访问: [http://localhost:5173](http://localhost:5173) （默认端口，实际以终端输出为准）

---

## 三、主要功能模块
- 人脸识别（录入、识别）
- 路面病害检测
- 交通数据统计与可视化
- 日志与告警

---

## 四、常见问题
- 如端口冲突，可在 `vite.config.js` 或 `uvicorn` 启动命令中修改端口。
- 前后端接口通过 `/api` 代理，无需手动更改跨域配置。

---

## 五、后续开发建议
- 可根据实际需求补充数据库、AI模型推理、日志落地、权限认证等功能。
- 详细功能实现请参考各自模块下的 `TODO` 注释。

---

如有问题欢迎随时反馈！ 