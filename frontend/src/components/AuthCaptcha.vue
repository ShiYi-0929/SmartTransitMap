<template>
  <div class="auth-captcha">
    <input 
      type="text" 
      placeholder="请输入验证码" 
      v-model="captchaValue" 
      class="captcha-input"
    />
  </div>
</template>

<script>
export default {
  name: 'AuthCaptcha',
  data() {
    return {
      captchaValue: ''
    };
  },
  methods: {
    refreshCaptcha() {
      // 实际项目中调用接口刷新验证码
      console.log('验证码已刷新');
    }
  },
  // 暴露验证码值供父组件获取
  computed: {
    currentValue() {
      return this.captchaValue;
    }
  }
};
</script>

<style scoped>
.auth-captcha {
  display: flex;
  align-items: center;
  gap: 10px;
}

.captcha-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}
</style>