import axios from 'axios'

export function registerFace(userId, file) {
  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('file', file)
  return axios.post('/api/face/register', formData)
}

export function verifyFace(userId, file) {
  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('file', file)
  return axios.post('/api/face/verify', formData)
} 