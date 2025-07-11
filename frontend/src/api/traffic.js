import axios from '@/utils/request'

export function getTrafficStats() {
  return axios.get('/traffic/stats')
}

export function getTrafficVisualization() {
  return axios.get('/traffic/visualization')
} 