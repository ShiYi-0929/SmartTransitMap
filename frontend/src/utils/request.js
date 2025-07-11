import router from '@/router';
import axios from 'axios';
import { ElNotification } from 'element-plus';

// 创建axios实例
const service = axios.create({
  // 在proxy中配置的代理前缀
  baseURL: '/api', 
  timeout: 10000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    const token = localStorage.getItem('token');
    if (token) {
      // 让每个请求携带自定义token
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    // 对请求错误做些什么
    console.log(error); // for debug
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    const res = response.data;
    if (response.status !== 200) {
      ElNotification({
        title: '错误',
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000,
      });
      return Promise.reject(new Error(res.message || 'Error'));
    } else {
      return res;
    }
  },
  error => {
    // 对响应错误做点什么
    console.log('err' + error); // for debug

    // 处理401错误（token过期）
    if (error.response && error.response.status === 401) {
      // 清除过期的认证信息
      localStorage.removeItem('token');
      localStorage.removeItem('user-class');
      
      // 跳转到登录页面
      router.push('/');
      
      ElNotification({
        title: '登录过期',
        message: '您的登录已过期，请重新登录',
        type: 'warning',
        duration: 3 * 1000,
      });
      
      return Promise.reject(error);
    }

    // 如果后端返回了具体的错误信息，则不再显示通用的错误提示
    // 让业务代码中的catch块去处理
    if (error.response && error.response.data && error.response.data.detail) {
        return Promise.reject(error);
    }

    ElNotification({
      title: '请求错误',
      message: error.message,
      type: 'error',
      duration: 5 * 1000,
    });
    return Promise.reject(error);
  }
);

export default service; 