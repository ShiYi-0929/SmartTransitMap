import api from "./index.js";

// 路面检测相关API
export const detectionAPI = {
  // 上传图片
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append("image", file);
    return api.post("/upload/image", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },

  // 开始检测
  startDetection: (data) => {
    return api.post("/detect", data);
  },

  // 获取检测结果
  getDetectionResult: (id) => {
    return api.get(`/results/${id}`);
  },

  // 获取告警信息
  getAlarms: () => {
    return api.get("/alarm");
  },

  // 获取统计数据
  getStatistics: () => {
    return api.get("/trend");
  },

  // 获取操作日志
  getLogs: () => {
    return api.get("/logs");
  },
};
