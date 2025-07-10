import axios from '@/utils/request';

export function login(userID, password) {
  return axios.post('/user/login', { userID, password });
}

export function register(username, password, email) {
  return axios.post('/user/register', { username, password, email });
}

export const sendVerificationCode = (email) => {
  return axios.post('/user/send-verification-code', { email });
};

export const verifyCode = (email, code) => {
  return axios.post('/user/verify-code', { email, code });
};

export const resetPassword = (email, code, new_password) => {
  return axios.post('/user/reset-password', { email, code, new_password });
};

export const getUserProfile = () => {
    return axios.get('/user/users/me');
};

export const updateUserProfile = (data) => {
    return axios.put('/user/users/me', data);
};

export const changePassword = (data) => {
  return axios.post('/user/change-password', data);
};

export const getPendingApplicationsCount = () => {
    return axios.get('/user/pending-applications-count');
}; 