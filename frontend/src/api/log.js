import request from '@/utils/request'

export function getLogs(query) {
  return request({
    url: '/log/',
    method: 'get',
    params: { search: query }
  })
}

export function deleteLog(logId) {
  return request.delete(`/log/${logId}`)
}

export function createLog({ logtype, description }, screenshot, video) {
  const formData = new FormData()
  formData.append('logtype', logtype)
  if (description) formData.append('description', description)
  if (screenshot) formData.append('screenshot', screenshot, 'screenshot.png')
  if (video) formData.append('video', video, 'video.webm')
  return request.post('/log/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function updateLog(logId, description) {
  return request.put(`/log/${logId}`, { description })
}

export function sendAlert(message) {
  return request.post('/log/alert', { message })
} 