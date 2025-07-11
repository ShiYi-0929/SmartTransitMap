import axios from 'axios'

export function ping() {
  return axios.get('/api/user/ping')
}

export function sendVerificationCode(email) {
  return axios.post('/api/user/send_code', { email });
}

export function login(loginData) {
  return axios.post('/api/user/login', loginData)
}

export function verifyCode(verificationData) {
  return axios.post('/api/user/verify_code', verificationData)
}

export function register(userData) {
  return axios.post('/api/user/register', userData)
}

export function resetPassword(resetData) {
  return axios.post('/api/user/reset_password', resetData)
} 