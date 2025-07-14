import axios from '@/utils/request';

// 获取待处理申请的数量
export const getPendingApplicationsCount = () => {
    return axios.get('/admin/pending-applications-count');
};

// 获取待处理的申请列表
export const getPendingApplications = () => {
    return axios.get('/admin/applications/pending');
};

// 获取已处理的申请列表
export const getProcessedApplications = () => {
    return axios.get('/admin/applications/processed');
};

// 处理申请（批准或拒绝）
export const processApplication = (applyId, approve) => {
    return axios.put(`/admin/applications/${applyId}`, null, { params: { approve } });
};

// 删除已处理的申请
export const deleteApplication = (applyId) => {
    return axios.delete(`/admin/applications/${applyId}`);
};

// 清空所有已处理的申请
export const clearProcessedApplications = () => {
    return axios.post('/admin/applications/processed/clear');
};

// 获取待处理人脸申请数量
export const getPendingFacesCount = () => {
    return axios.get('/face/faces/count?status=pending');
};

// 申请成为管理员
export const applyForAdmin = () => {
    return axios.post('/admin/apply-for-admin');
}; 