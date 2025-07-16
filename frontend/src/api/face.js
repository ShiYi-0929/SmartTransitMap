import request from '../utils/request'

// 人脸识别 - 注册
export function registerFace(data) {
  return request({
    url: '/face/register',
    method: 'post',
    data
  })
}

// 人脸识别 - 验证
export function verifyFace(data) {
  return request({
    url: '/face/verify',
    method: 'post',
    data
  })
}

export function rejectFace(personId) {
  return request({
    url: `/face/reject/${personId}`,
    method: 'post'
  });
}

// 新增：用户确认后清理自己的人脸数据
export function cleanupFaceData() {
  return request({
    url: '/face/cleanup',
    method: 'post'
  });
} 