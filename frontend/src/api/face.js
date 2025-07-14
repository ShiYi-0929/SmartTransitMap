import axios from '@/utils/request'

export function registerFace(userId, file) {
  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('file', file)
  return axios.post('/face/register', formData)
}

export function verifyFace(userId, file) {
  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('file', file)
  return axios.post('/face/verify', formData)
}

export function rejectFace(personId) {
  return axios.post(`/face/reject/${personId}`);
}

// 新增：用户确认后清理自己的人脸数据
export function cleanupFaceData() {
  return axios.post('/face/cleanup');
} 