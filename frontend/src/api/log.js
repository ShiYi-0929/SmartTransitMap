import axios from 'axios'

export function getLogs() {
  return axios.get('/api/log/logs')
}

export function sendAlert(message) {
  return axios.post('/api/log/alert', { message })
} 