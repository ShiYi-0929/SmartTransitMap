import axios from '@/utils/request'

export function detectRoadDamage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post('/road/detect', formData)
}

export function getDetectionResult(taskId) {
  return axios.get(`/road/result/${taskId}`)
} 