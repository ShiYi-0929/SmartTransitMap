import axios from 'axios'

export function getTrafficStats() {
  return axios.get('/api/traffic/stats')
}

export function getTrafficVisualization() {
  return axios.get('/api/traffic/visualization')
} 