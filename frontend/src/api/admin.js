import axios from '@/utils/request';

// 申请成为管理员
export const applyForAdmin = () => {
  return axios.post('/admin/apply-for-admin');
};

// 获取待处理的申请列表
export const getPendingApplications = () => {
  return axios.get('/admin/applications/pending');
};

// 获取已处理的申请列表
export const getProcessedApplications = () => {
  return axios.get('/admin/applications/processed');
};

// 处理申请
export const processApplication = (applyId, approve) => {
  return axios.put(`/admin/applications/${applyId}`, null, {
    params: {
      approve: approve
    }
  });
};

// 删除单条已处理的申请
export const deleteApplication = (applyId) => {
  return axios.delete(`/admin/applications/${applyId}`);
};

// 清空所有已处理的申请
export const clearProcessedApplications = () => {
  return axios.post('/admin/applications/processed/clear');
}; 