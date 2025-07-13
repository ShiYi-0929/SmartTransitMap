<template>
  <div class="auth-form">
    <slot name="title"></slot>
    <form @submit.prevent="handleSubmit">
      <slot name="fields"></slot>
      <slot name="actions"></slot>
    </form>
  </div>
</template>

<script>
export default {
  name: "AuthForm",
  methods: {
    handleSubmit() {
      // 可在子组件中重写此方法实现表单提交逻辑
      console.log("表单提交触发");
    },
  },
};
</script>

<style scoped>
.auth-form {
  width: 300px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 5px;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
</style>
