import axios from 'axios'

export function ping() {
  return axios.get('/api/user/ping')
}

export function sendVerificationCode(email) {
  return axios.post('/api/user/send_code', { email });
} 