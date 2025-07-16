import axios from '@/utils/request';

export function login(userID, password) {
  return axios.post('/user/login', { userID, password });
}

export function loginByCode(email, code) {
  return axios.post('/user/login-by-code', { email, code });
}

export function register(username, password, email, code) {
  return axios.post('/user/register', { username, password, email, code });
}

export const sendVerificationCode = (email) => {
  return axios.post('/user/send-verification-code', { email });
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
  return axios.post('/user/users/me/change-password', data);
};

export const getUserStatus = () => {
  return axios.get('/user/users/me/status');
}; 