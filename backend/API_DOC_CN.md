# 人脸识别后端接口文档

> 基础地址：`http://localhost:8000`

| 方法 | 路径 | 描述 |
| ---- | ---- | ---- |
| GET  | `/` | 运行状态自检 |
| POST | `/register` | 录入 / 更新人脸 |
| POST | `/verify` | 验证人脸身份 |
| POST | `/check_face_in_frame` | 检测人脸是否位于中心框 |
| GET  | `/faces` | 获取全部用户信息列表 |
| PUT  | `/faces/{person_id}` | 更新用户姓名（目前与 ID 保持一致）|
| DELETE | `/faces/{person_id}` | 删除指定用户及其全部图片 |
| DELETE | `/faces` | 清空所有人脸数据 |
| GET | `/faces/{person_id}/images` | 获取用户全部图片 URL |
| DELETE | `/faces/{person_id}/images/{filename}` | 删除用户单张图片 |
| GET | `/images/{filename}` | 访问已保存的静态图片 |

---

## 1. 运行状态
```
GET /
```
### 响应示例
```json
{
  "status": "running",
  "faces_in_db": 3
}
```

---
## 2. 录入 /register
```
POST /register
Content-Type: application/json
```
### 请求字段
| 字段 | 类型 | 说明 | 必填 |
| ---- | ---- | ---- | ---- |
| `person_id` | string | 用户唯一 ID（前端亦作显示） | ✅ |
| `images` | string[] (dataURL) | **推荐**：多张 base64 dataURL | 二选一 |
| `image` | string (dataURL) | 单张 base64 dataURL | 二选一 |

> **注意**：后端会自动裁剪人脸区域并提取特征；若 `person_id` 已存在则会更新其特征并追加图片。

### 响应示例
```json
{
  "msg": "ok",
  "faces_in_db": 4,
  "face_saved": true,
  "images_received": 3,
  "person_id": "123"
}
```

---
## 3. 验证 /verify
```
POST /verify
Content-Type: application/json
```
### 请求字段
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `image` | string (dataURL) | 待验证的单张图片 |

### 响应示例
```json
{
  "result": "123",      // 识别到的 person_id，或 "unknown"
  "person_id": "123",   // 同上，未知时为 null
  "distance": 0.38,      // 特征欧氏距离
  "threshold": 0.5       // 判定阈值
}
```

---
## 4. 检测人脸位置 /check_face_in_frame
```
POST /check_face_in_frame
Content-Type: application/json
```
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `image` | string (dataURL) | 摄像头当前帧 |

### 响应示例
```json
{
  "in_frame": true,
  "reason": null
}
```
当未检测到人脸时 `in_frame = false`，`reason` 返回 `"no_face_detected"`。

---
## 5. 获取用户列表 /faces
```
GET /faces
```
### 响应示例
```json
{
  "faces": [
    { "id": "123", "name": "123", "image": "/images/20250710141635_0_fffcb1.png", "images": "20250710141635_0_fffcb1.png,20250710141635_1_935173.png" },
    { "id": "789", "name": "789", ... }
  ]
}
```

---
## 6. 更新姓名 /faces/{person_id}
```
PUT /faces/{person_id}
Content-Type: application/json
```
| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `name` | string | 新姓名（目前与 ID 保持一致） |

### 响应示例
```json
{ "msg": "姓名已更新", "person_id": "123", "name": "new_name" }
```

---
## 7. 删除用户 /faces/{person_id}
```
DELETE /faces/{person_id}
```
删除数据库记录、特征、以及其全部图片。

### 响应示例
```json
{ "msg": "用户已删除", "person_id": "123" }
```

---
## 8. 清空全部 /faces
```
DELETE /faces
```
删除所有 encodings.pkl / CSV / 图片文件。

### 响应示例
```json
{ "msg": "所有人脸数据已清空" }
```

---
## 9. 获取用户所有图片 /faces/{person_id}/images
```
GET /faces/{person_id}/images
```
### 响应示例
```json
{ "images": ["/images/20250710141635_0_fffcb1.png", "..." ] }
```

---
## 10. 删除单张图片 /faces/{person_id}/images/{filename}
```
DELETE /faces/{person_id}/images/{filename}
```
### 响应示例
```json
{ "msg": "图片已删除", "remaining": "20250710141635_0_fffcb1.png" }
```

---
## 11. 访问静态图片 /images/{filename}
`/images` 路径挂载静态文件，浏览器直接访问返回图片数据。

---

### 返回状态码约定
| 码 | 含义 |
| -- | ---- |
| 200 | 成功 |
| 400 | 请求参数错误（如缺字段、未检测到人脸） |
| 404 | 资源不存在 |
| 500 | 服务内部错误 |

---
> 文档版本：v1.0  
> 最后更新：2025-07-10 