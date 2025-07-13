import axios from '@/utils/request'

export function getLogs() {
  return axios.get('/log/logs')
}

export function sendAlert(message) {
  return axios.post('/log/alert', { message })
} 