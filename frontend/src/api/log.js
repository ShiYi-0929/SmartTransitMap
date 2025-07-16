import request from '@/utils/request';

export function getLogs(query) {
  return request({
    url: '/log/',
    method: 'get',
    params: { search: query }
  });
}

export function deleteLog(logId) {
  // 修正API路径
  return request.delete(`/log/${logId}`);
}

/**
 * 创建一条新的系统日志，并可选地上传媒体文件。
 * @param {Object} logData - 包含日志信息的对象。
 * @param {string} logData.logtype - 日志类型。
 * @param {string} [logData.description] - 日志描述。
 * @param {Blob} [screenshot] - 截图文件Blob。
 * @param {Blob} [video] - 视频文件Blob。
 * @returns {Promise}
 */
export function createLog({ logtype, description }, screenshot, video) {
  const formData = new FormData();
  formData.append('logtype', logtype);
  if (description) {
    formData.append('description', description);
  }
  if (screenshot) {
    formData.append('screenshot', screenshot, 'screenshot.png');
  }
  if (video) {
    formData.append('video', video, 'video.webm');
  }

  // 使用正确的路径 /log/
  return request.post('/log/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

export function updateLog(logId, description) {
  return request.put(`/log/${logId}`, { description });
}

export function sendAlert(message) {
  return request.post('/log/alert', { message })
} 