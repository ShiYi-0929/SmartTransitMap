import axios from 'axios'

export function detectRoadDamage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post('/api/road/detect', formData)
}

export function getDetectionResult(taskId) {
  return axios.get(`/api/road/result/${taskId}`)
} 