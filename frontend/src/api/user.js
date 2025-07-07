import axios from 'axios'

export function ping() {
  return axios.get('/api/user/ping')
} 