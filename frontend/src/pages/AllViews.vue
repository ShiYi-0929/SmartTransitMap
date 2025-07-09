<template>
  <div class="all-views-container">
    <!-- AuthLogin View -->
    <div v-if="currentView === 'login'">
      <div class="auth-page" :style="authPageStyle('bg5')">
        <AuthNavbar />
        <div class="auth-content">
          <AuthSlide :images="slideImages" />
          <AuthForm>
            <template #title>
              <div class="title-container">
                <h2>账号密码登录</h2>
                <div class="login-options">
                  <span @click="navigateTo('captcha-login')">验证码登录</span>
                  <span @click="alertNotAvailable">扫码登录</span>
                </div>
              </div>
            </template>
            <template #fields>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-user"></i>
                  <input type="text" v-model="username" placeholder="用户名" class="input-field" />
                </div>
              </div>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-lock"></i>
                  <input :type="passwordVisible ? 'text' : 'password'" v-model="password" placeholder="密码" class="input-field" />
                  <i class="fa" :class="passwordVisible ? 'fa-eye-slash' : 'fa-eye'" @click="togglePasswordVisibility"></i>
                </div>
              </div>
              <div class="form-group captcha-group">
                <canvas ref="captchaCanvas" @click="generateCaptcha" class="captcha-canvas"></canvas>
                <input type="text" v-model="captchaInput" placeholder="请输入验证码" class="input-field captcha-input-field" />
                <a href="#" @click.prevent="generateCaptcha">看不清？换一张</a>
              </div>
            </template>
            <template #actions>
              <button @click="handleLogin" :disabled="!isLoginFormValid">登录</button>
              <div class="extra-options">
                <a href="#" @click.prevent="navigateTo('find-password')">忘记密码？</a>
                <a href="#" @click.prevent="navigateTo('register')">立即注册</a>
              </div>
            </template>
          </AuthForm>
        </div>
        
      </div>
    </div>

    <!-- CaptchaLogin View -->
    <div v-if="currentView === 'captcha-login'">
      <div class="auth-page" :style="authPageStyle('bg5')">
        <AuthNavbar />
        <div class="auth-content">
          <AuthSlide :images="slideImages" />
          <AuthForm>
            <template #title>
              <div class="title-container">
                <h2>验证码登录</h2>
                <div class="login-options">
                  <span @click="navigateTo('login')">密码登录</span>
                  <span @click="alertNotAvailable">扫码登录</span>
                </div>
              </div>
            </template>
            <template #fields>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-phone"></i>
                  <input type="text" v-model="account" placeholder="邮箱" class="input-field" />
                </div>
              </div>
              <div class="form-group captcha-group">
                <input type="text" v-model="captchaInput" placeholder="请输入验证码" class="input-field captcha-input-field" />
                <button :disabled="countdown > 0 || !account" @click="getCaptcha" class="get-captcha-btn">
                  {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
                </button>
              </div>
            </template>
            <template #actions>
              <button @click="handleCaptchaLogin" :disabled="!account || !captchaInput">登录</button>
              <div class="extra-options">
                <a href="#" @click.prevent="navigateTo('find-password')">忘记密码？</a>
                <a href="#" @click.prevent="navigateTo('register')">立即注册</a>
              </div>
            </template>
          </AuthForm>
        </div>
        
      </div>
    </div>

    <!-- QrCodeLogin View - REMOVED -->

    <!-- Register View -->
    <div v-if="currentView === 'register'">
      <div class="auth-page" :style="authPageStyle('bg5')">
        <AuthNavbar />
        <div class="auth-content">
          <AuthSlide :images="slideImages" />
          <AuthForm>
            <template #title>
              <div class="title-container">
                <h2>新用户注册</h2>
                <span @click="navigateTo('login')" class="link-style">已有账号？立即登录</span>
              </div>
            </template>
            <template #fields>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-user"></i>
                  <input type="text" v-model="username" placeholder="用户名" class="input-field" />
                </div>
              </div>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-lock"></i>
                  <input :type="passwordVisible ? 'text' : 'password'" v-model="password" placeholder="密码" class="input-field" />
                  <i class="fa" :class="passwordVisible ? 'fa-eye-slash' : 'fa-eye'" @click="togglePasswordVisibility"></i>
                </div>
              </div>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-lock"></i>
                  <input :type="confirmPasswordVisible ? 'text' : 'password'" v-model="confirmPassword" placeholder="确认密码" class="input-field" />
                  <i class="fa" :class="confirmPasswordVisible ? 'fa-eye-slash' : 'fa-eye'" @click="toggleConfirmPasswordVisibility"></i>
                </div>
              </div>
              <div class="form-group captcha-group">
                <canvas ref="captchaCanvas" @click="generateCaptcha" class="captcha-canvas"></canvas>
                <input type="text" v-model="captchaInput" placeholder="请输入验证码" class="input-field captcha-input-field" />
                <a href="#" @click.prevent="generateCaptcha">看不清？换一张</a>
              </div>
            </template>
            <template #actions>
              <button @click="handleRegister" :disabled="!isRegisterFormValid">注册</button>
              <!-- 移除了这里的 "extra-options" 和同意协议的复选框 -->
            </template>
          </AuthForm>
        </div>
        
      </div>
    </div>

    <!-- BindAccount View -->
    <div v-if="currentView === 'bind-account'">
      <div class="auth-page" :style="authPageStyle('bg5')">
        <AuthNavbar />
        <div class="auth-content">
          <AuthSlide :images="slideImages" />
          <AuthForm>
            <template #title>
              <div class="title-container">
                <h2>账号绑定</h2>
                <span @click="navigateTo('login')">已有账号？立即登录</span>
              </div>
            </template>
            <template #fields>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-phone"></i>
                  <input type="text" v-model="account" placeholder="请输入邮箱" class="input-field" />
                </div>
              </div>
              <div class="form-group captcha-group">
                <input type="text" v-model="captchaInput" placeholder="请输入验证码" class="input-field captcha-input-field" />
                <button :disabled="countdown > 0 || !account" @click="getCaptcha" class="get-captcha-btn">
                  {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
                </button>
              </div>
            </template>
            <template #actions>
              <button @click="handleBind" :disabled="isLoading">
                {{ isLoading ? '绑定中...' : '立即绑定' }}
              </button>
              <div class="extra-options">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="agreeTerms" />
                  <span class="checkbox-custom"></span>
                  <span>我已阅读并同意 <a href="#" @click.prevent="showTerms">用户协议</a> 和 <a href="#" @click.prevent="showPrivacy">隐私政策</a></span>
                </label>
              </div>
            </template>
          </AuthForm>
        </div>
        
      </div>
    </div>

    <!-- FindPassword View -->
    <div v-if="currentView === 'find-password'">
      <div class="auth-page" :style="authPageStyle('bg5')">
        <AuthNavbar />
        <div class="auth-content">
          <AuthSlide :images="slideImages" />
          <AuthForm>
            <template #title>
              <div class="title-container">
                <h2>找回密码</h2>
                <span @click="navigateTo('login')" class="link-style">返回登录</span>
              </div>
            </template>
            <template #actions>
              <div class="reset-options">
                <button @click="navigateTo('find-password-by-email')">
                  <i class="fa fa-envelope"></i>
                  <span>邮箱找回</span>
                </button>
              </div>
            </template>
          </AuthForm>
        </div>
        
      </div>
    </div>

    <!-- FindPasswordByEmail View -->
    <div v-if="currentView === 'find-password-by-email'">
      <div class="auth-page" :style="authPageStyle('bg5')">
        <AuthNavbar />
        <div class="auth-content">
          <AuthSlide :images="slideImages" />
          <AuthForm>
            <template #title>
              <div class="title-container">
                <h2>邮箱找回密码</h2>
                <span @click="navigateTo('find-password')" class="link-style">返回选择</span>
              </div>
            </template>
            <template #fields>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-envelope"></i>
                  <input type="text" v-model="email" placeholder="请输入注册邮箱" class="input-field" />
                </div>
              </div>
              <div class="form-group captcha-group">
                <input type="text" v-model="captchaInput" placeholder="请输入验证码" class="input-field captcha-input-field" />
                <button :disabled="countdown > 0 || !email" @click="getCaptcha" class="get-captcha-btn">
                  {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
                </button>
              </div>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-lock"></i>
                  <input :type="newPasswordVisible ? 'text' : 'password'" v-model="newPassword" placeholder="请输入新密码" class="input-field" />
                  <i class="fa" :class="newPasswordVisible ? 'fa-eye-slash' : 'fa-eye'" @click="toggleNewPasswordVisibility"></i>
                </div>
              </div>
              <div class="form-group">
                <div class="input-container">
                  <i class="fa fa-lock"></i>
                  <input :type="confirmNewPasswordVisible ? 'text' : 'password'" v-model="confirmNewPassword" placeholder="请确认新密码" class="input-field" />
                  <i class="fa" :class="confirmNewPasswordVisible ? 'fa-eye-slash' : 'fa-eye'" @click="toggleConfirmNewPasswordVisibility"></i>
                </div>
              </div>
            </template>
            <template #actions>
              <button @click="resetPasswordByEmail">确认重置</button>
            </template>
          </AuthForm>
        </div>
        
      </div>
    </div>

    <!-- Terms Modal -->
    <div v-if="showTermsModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>用户协议</h3>
          <button @click="showTermsModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="terms-content">
            <h4>1. 服务条款的接受</h4>
            <p>当您使用本网站服务时，即表示您同意接受本服务条款的所有条款和条件。如果您不同意本服务条款的任何部分，请勿使用本网站服务。</p>
            <h4>2. 服务说明</h4>
            <p>本网站通过互联网向用户提供各种服务，包括但不限于信息发布、在线交流、电子商务等。本网站保留随时更改或中断服务而不需通知用户的权利。本网站不保证服务不会中断，对服务的及时性、安全性、准确性也不作担保。</p>
            <h4>3. 用户行为</h4>
            <p>用户在使用本网站服务时必须遵守中华人民共和国的相关法律法规，不得利用本网站服务进行任何违法或不当的行为，包括但不限于：发布虚假信息、侵犯他人知识产权、传播淫秽色情内容、进行诈骗活动等。</p>
            <h4>4. 隐私政策</h4>
            <p>本网站尊重用户的隐私，将按照本网站的隐私政策收集、使用和保护用户的个人信息。用户在使用本网站服务时，即表示同意本网站按照本隐私政策收集、使用和保护您的个人信息。</p>
            <h4>5. 免责声明</h4>
            <p>本网站对因不可抗力、黑客攻击、系统故障等原因导致的服务中断或用户损失不承担责任。本网站对用户发布的内容的真实性、准确性、合法性不承担任何责任。用户对自己在本网站上的行为承担全部法律责任。</p>
            <h4>6. 版权声明</h4>
            <p>本网站上的所有内容，包括但不限于文字、图片、音频、视频等，均受版权保护。未经本网站书面许可，任何单位或个人不得复制、传播、修改本网站上的任何内容。</p>
            <h4>7. 服务条款的修改</h4>
            <p>本网站有权随时修改本服务条款，并在本网站上公布。用户在使用本网站服务时，应随时关注本服务条款的修改情况。如果用户继续使用本网站服务，即表示同意接受修改后的服务条款。</p>
            <h4>8. 法律适用和管辖</h4>
            <p>本服务条款的解释、适用和争议的解决均适用中华人民共和国的法律。如发生争议，双方应协商解决；协商不成的，任何一方均有权向本网站所在地的人民法院提起诉讼。</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showTermsModal = false">我已阅读并同意</button>
        </div>
      </div>
    </div>

    <!-- Privacy Modal -->
    <div v-if="showPrivacyModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>隐私政策</h3>
          <button @click="showPrivacyModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="privacy-content">
            <h4>1. 引言</h4>
            <p>本网站尊重并保护所有使用服务用户的个人隐私权。为了给您提供更准确、更有个性化的服务，本网站会按照本隐私政策的规定收集、使用和保护您的个人信息。请在使用本网站服务前仔细阅读本隐私政策，特别是关于我们收集哪些信息、如何使用这些信息、向谁披露这些信息以及您对这些信息享有哪些权利的条款。如果您不同意本隐私政策的任何内容，您应立即停止使用本网站服务。当您使用本网站的服务时，即表示您同意我们按照本隐私政策规定收集、使用、存储和披露您的个人信息。</p>
            <h4>2. 适用范围</h4>
            <p>(a) 在您注册本网站账号时，您根据本网站要求提供的个人注册信息；</p>
            <p>(b) 在您使用本网站网络服务，或访问本网站平台网页时，本网站自动接收并记录的您的浏览器和计算机上的信息，包括但不限于您的IP地址、浏览器的类型、使用的语言、访问日期和时间、软硬件特征信息及您需求的网页记录等数据；</p>
            <p>(c) 本网站通过合法途径从商业伙伴处取得的用户个人数据。</p>
            <h4>3. 信息收集和使用</h4>
            <p>本网站收集您的个人信息的主要目的是为您提供个性化的服务，包括但不限于：</p>
            <p>(a) 帮助您注册成为本网站的用户；</p>
            <p>(b) 向您提供您需要的服务；</p>
            <p>(c) 理解您的需求，改进我们的服务；</p>
            <p>(d) 向您发送产品和服务信息，或与本网站业务相关的商业信息；</p>
            <p>(e) 允许您参与我们的调查、竞赛和促销活动；</p>
            <p>(f) 其他符合法律规定和行业惯例的用途。</p>
            <h4>4. 信息披露</h4>
            <p>在以下情况下，本网站可能会披露您的个人信息：</p>
            <p>(a) 获得您的明确授权；</p>
            <p>(b) 根据法律、法规、司法程序或政府主管部门的强制性要求；</p>
            <p>(c) 在紧急情况下，为维护本网站、本网站用户或公众的合法权益；</p>
            <p>(d) 与本网站的关联公司、合作伙伴或服务提供商分享，以提供您所请求的服务；</p>
            <p>(e) 在本网站发生合并、收购、重组、破产清算等情况时，如涉及到个人信息的转让，我们会要求新的持有您个人信息的公司、组织继续受本隐私政策的约束，否则我们将要求该公司、组织重新向您征求授权同意。</p>
            <h4>5. 信息存储和保护</h4>
            <p>本网站采用行业标准的安全技术和程序来保护您的个人信息不被未经授权的访问、使用或泄露。然而，请注意，没有任何一种互联网传输方式或电子存储方式是100%安全的，因此我们不能保证您的个人信息绝对安全。如果发生信息安全事件，我们将按照相关法律法规的要求及时通知您并采取相应的措施。</p>
            <h4>6. 用户权利</h4>
            <p>您有权访问、更正和删除您的个人信息，以及限制或反对某些个人信息处理活动。您也有权撤回您之前给予的同意。如果您需要行使这些权利，请通过本网站提供的联系方式与我们联系。我们将在合理的时间内响应您的请求。</p>
            <h4>7. 隐私政策的更新</h4>
            <p>本网站可能会不时更新本隐私政策。当我们对隐私政策进行重大变更时，我们将通过在本网站上发布新的隐私政策或其他适当的方式通知您。请定期查看本隐私政策，以了解我们如何收集、使用和保护您的信息。您继续使用本网站服务即表示您同意接受更新后的隐私政策的约束。</p>
            <h4>8. 联系我们</h4>
            <p>如果您对本隐私政策有任何疑问、意见或建议，请通过本网站提供的联系方式与我们联系。我们将尽快回复您的咨询。</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showPrivacyModal = false">我已阅读并同意</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AuthNavbar from '@/components/AuthNavbar.vue';
import AuthForm from '@/components/AuthForm.vue';
import AuthFooter from '@/components/AuthFooter.vue';
import AuthSlide from '@/components/AuthSlide.vue'; // Assuming AuthSlide component exists
import { sendVerificationCode, verifyCode, login, register, resetPassword } from '@/api/user.js';

// Importing images
import bg1 from '@/assets/bg1.png';
import bg2 from '@/assets/bg2.png';
import bg3 from '@/assets/bg3.png';
import bg4 from '@/assets/bg4.png';
import bg5 from '@/assets/bg5.png';
import accountIcon from '@/assets/account-icon.png';
import qrcode from '@/assets/qrcode-icon.png'; // Assuming this is the correct qrcode image

export default {
  components: {
    AuthNavbar,
    AuthForm,
    AuthFooter,
    AuthSlide
  },
  data() {
    return {
      // 当前显示的视图
      currentView: 'login',
      // 登录相关数据
      username: '',
      password: '',
      passwordVisible: false,
      // 暂存注册数据
      registrationData: {
        username: '',
        password: ''
      },
      // 验证码相关数据
      captchaInput: '',
      generatedCaptchaText: '',
      // 注册相关数据
      confirmPassword: '',
      confirmPasswordVisible: false,
      // 绑定账号相关数据
      account: '',
      agreeTerms: false,
      // 找回密码相关数据
      email: '',
      newPassword: '',
      newPasswordVisible: false,
      confirmNewPassword: '',
      confirmNewPasswordVisible: false,
      // 倒计时相关
      countdown: 0,
      // 模态框相关
      showTermsModal: false,
      showPrivacyModal: false,
      // 加载状态
      isLoading: false,
      accountIcon: accountIcon,
      qrcode: qrcode,
      // 轮播图图片
      slideImages: [
        bg1,
        bg2,
        bg3,
        bg4
      ],
      backgroundImages: {
        bg1: bg1,
        bg2: bg2,
        bg3: bg3,
        bg4: bg4,
        bg5: bg5,
        bg6: bg1, // default
        bg7: bg2, // default
        bg8: bg3  // default
      }
    };
  },
  computed: {
    // 表单验证相关计算属性
    isLoginFormValid() {
      return this.username && this.password && this.captchaInput;
    },
    isRegisterFormValid() {
      return (
        this.username &&
        this.password &&
        this.confirmPassword &&
        this.password === this.confirmPassword &&
        this.captchaInput
        // 移除了 this.agreeTerms 验证
      );
    },
    isBindAccountFormValid() {
      return this.account && this.captchaInput && this.agreeTerms;
    },
    isFindPasswordByEmailFormValid() {
      return (
        this.email &&
        this.captchaInput &&
        this.newPassword &&
        this.confirmNewPassword &&
        this.newPassword === this.confirmNewPassword
      );
    }
  },
  methods: {
    // 导航到指定视图
    navigateTo(view) {
      this.currentView = view;
      // 重置表单数据
      this.resetFormData();
      // 如果是登录或注册视图，生成验证码
      if (view === 'login' || view === 'register') {
        this.$nextTick(() => {
          this.generateCaptcha();
        });
      }
    },
    // 重置表单数据
    resetFormData() {
      this.username = '';
      this.password = '';
      this.passwordVisible = false;
      this.captchaInput = '';
      this.generatedCaptchaText = '';
      this.confirmPassword = '';
      this.confirmPasswordVisible = false;
      this.account = '';
      this.agreeTerms = false;
      this.email = '';
      this.newPassword = '';
      this.newPasswordVisible = false;
      this.confirmNewPassword = '';
      this.confirmNewPasswordVisible = false;
      this.countdown = 0;
      this.isLoading = false;
    },
    // 生成验证码
    generateCaptcha() {
      const canvas = this.$refs.captchaCanvas;
      if (!canvas) {
        this.$nextTick(this.generateCaptcha);
        return;
      }
      // Set canvas resolution to match its display size to avoid distortion
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      const ctx = canvas.getContext('2d');
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      let captchaText = '';
      for (let i = 0; i < 4; i++) {
        captchaText += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      this.generatedCaptchaText = captchaText;

      // Clear and draw background
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#f0f0f0';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw text
      ctx.font = 'bold 28px Arial'; // Adjusted font size for better fit
      ctx.fillStyle = '#333';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(captchaText, canvas.width / 2, canvas.height / 2 + 2); // Adjust vertical alignment

      // Add more and longer noise lines
      for (let i = 0; i < 8; i++) { // Increased from 3 to 8 lines
        ctx.strokeStyle = `rgb(${Math.random()*200},${Math.random()*200},${Math.random()*200})`;
        ctx.lineWidth = Math.random() * 1.5;
        ctx.beginPath();
        // Allow lines to start and end slightly off-canvas to appear longer
        ctx.moveTo(Math.random() * canvas.width * 1.4 - canvas.width * 0.2, Math.random() * canvas.height);
        ctx.lineTo(Math.random() * canvas.width * 1.4 - canvas.width * 0.2, Math.random() * canvas.height);
        ctx.stroke();
      }
    },
    // 切换密码可见性
    togglePasswordVisibility() {
      this.passwordVisible = !this.passwordVisible;
    },
    toggleConfirmPasswordVisibility() {
      this.confirmPasswordVisible = !this.confirmPasswordVisible;
    },
    toggleNewPasswordVisibility() {
      this.newPasswordVisible = !this.newPasswordVisible;
    },
    toggleConfirmNewPasswordVisibility() {
      this.confirmNewPasswordVisible = !this.confirmNewPasswordVisible;
    },
    // 验证验证码
    validateCaptcha() {
      if (this.captchaInput.toLowerCase() !== this.generatedCaptchaText.toLowerCase()) {
        alert('验证码不正确!');
        this.generateCaptcha();
        this.captchaInput = '';
        return false;
      }
      return true;
    },
    // 获取验证码（短信/邮件）
    async getCaptcha() { // 标记为异步函数
      if (this.countdown > 0) return;

      let isValid = false;
      let targetAccount = '';
      let isEmail = false;

      // 确定目标账户和类型
      if (this.currentView === 'captcha-login' || this.currentView === 'bind-account') {
        targetAccount = this.account;
      } else if (this.currentView === 'find-password-by-email') {
        targetAccount = this.email;
      }
      
      // 验证格式
      const phoneRegex = /^1[3-9]\d{9}$/;
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

      if (emailRegex.test(targetAccount)) {
        isEmail = true;
        isValid = true;
      } else if (phoneRegex.test(targetAccount)) {
        // 在这里可以添加发送短信验证码的逻辑 (如果需要)
        alert('短信功能暂未实现，请输入邮箱获取验证码。');
        return;
      } else {
        alert('请输入正确的手机号或邮箱');
        return;
      }
      
      if (!isValid) return;

      // 如果是邮箱，调用后端API
      if (isEmail) {
        try {
          // 调用API发送邮件
          const response = await sendVerificationCode(targetAccount);
          alert(response.data.message || '验证码已发送，请查收。');
          
          // 开始倒计时
          this.countdown = 60;
          const timer = setInterval(() => {
            this.countdown--;
            if (this.countdown <= 0) clearInterval(timer);
          }, 1000);

        } catch (error) {
          console.error('发送验证码失败:', error);
          const detail = error.response?.data?.detail || '发送失败，请稍后重试。';
          alert(`发送验证码失败: ${detail}`);
          return; // 发送失败，不开始倒计时
        }
      }
    },
    // 验证账号（手机号或邮箱格式）
    validateAccount() {
      const phoneRegex = /^1[3-9]\d{9}$/;
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      
      if (phoneRegex.test(this.account)) {
        return true;
      } else if (emailRegex.test(this.account)) {
        return true;
      } else {
        alert('请输入正确的手机号或邮箱');
        return false;
      }
    },
    // 处理登录
    async handleLogin() {
      if (!this.validateCaptcha()) return;
      if (!this.isLoginFormValid) {
          alert('请输入用户名、密码和验证码。');
          return;
      }
      try {
        const response = await login(this.username, this.password);
        const token = response.data.access_token;
        localStorage.setItem('user-token', token);
        alert('登录成功!');
        this.$router.push('/home');
      } catch (error) {
        const detail = error.response?.data?.detail || '登录失败，请检查您的凭据。';
        alert(`登录失败: ${detail}`);
        this.generateCaptcha(); // 刷新验证码
        this.captchaInput = '';
      }
    },
    // 处理验证码登录
    async handleCaptchaLogin() {
      try {
        await verifyCode(this.account, this.captchaInput);
        // 验证通过后，再执行登录逻辑
        alert('登录成功!');
        localStorage.setItem('user-token', 'your-secret-token');
        this.$router.push('/home');
      } catch (error) {
        const detail = error.response?.data?.detail || '验证失败，请重试。';
        alert(detail);
      }
    },
    // 处理注册
    handleRegister() {
      if (!this.isRegisterFormValid) {
        alert('请确保所有字段都已正确填写，且两次输入的密码一致。');
        return;
      }

      if(this.validateCaptcha()) {
        // 暂存用户名和密码
        this.registrationData.username = this.username;
        this.registrationData.password = this.password;
        this.navigateTo('bind-account');
      }
    },
    // 处理账号绑定 (现在是注册的最后一步)
    async handleBind() {
      if (!this.validateForm()) return;
      this.isLoading = true;

      try {
        // 步骤1：验证邮箱验证码
        await verifyCode(this.account, this.captchaInput);

        // 步骤2：验证码通过后，提交注册信息
        // 从暂存数据中获取用户名和密码
        const response = await register(this.registrationData.username, this.registrationData.password, this.account);
        
        alert(`${response.data.message}！现在可以用新账号登录了。`);
        this.navigateTo('login'); // 跳转到登录页面

      } catch (error) {
        const detail = error.response?.data?.detail || '操作失败，请重试。';
        alert(`注册失败: ${detail}`);
      } finally {
        this.isLoading = false;
      }
    },
    // 表单验证
    validateForm() {
      if (!this.account) {
        alert('请输入手机号或邮箱');
        return false;
      }
      if (!this.captchaInput) {
        alert('请输入验证码');
        return false;
      }
      if (!this.agreeTerms) {
        alert('请同意用户协议和隐私政策');
        return false;
      }
      return true;
    },
    // 显示用户协议
    showTerms() {
      this.showTermsModal = true;
    },
    // 显示隐私政策
    showPrivacy() {
      this.showPrivacyModal = true;
    },
    // 邮箱找回密码
    async resetPasswordByEmail() {
      if (!this.isFindPasswordByEmailFormValid) {
        alert('请确保所有字段都已正确填写，且两次输入的新密码一致。');
        return;
      }
      try {
        // 调用后端的重置密码接口
        const response = await resetPassword(this.email, this.captchaInput, this.newPassword);
        alert(response.data.message || '密码重置成功！');
        this.navigateTo('login');
      } catch(error) {
        const detail = error.response?.data?.detail || '操作失败，请重试。';
        alert(`密码重置失败: ${detail}`);
      }
    },
    alertNotAvailable() {
      alert('该功能暂未开放');
    },
    // 设置认证页面的背景样式
    authPageStyle(bgName) {
      const bgImage = this.backgroundImages[bgName] || this.backgroundImages['bg5'];
      return {
        backgroundImage: `url(${bgImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      };
    }
  },
  mounted() {
    // 初始化验证码
    this.generateCaptcha();
  },
  watch: {
    // 当视图切换时，重新生成验证码
    currentView(newView) {
      if (newView === 'login' || newView === 'register') { // 从这里移除了 'find-password'
        this.$nextTick(() => {
          this.generateCaptcha();
        });
      }
    }
  }
};
</script>

<style scoped>
/* 基础样式 */
.all-views-container {
  min-height: 100vh;
}

.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative; /* For the overlay */
  z-index: 0;
}

.auth-page::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.2); /* Lighter overlay */
  z-index: 1; /* Overlay on top of background */
}

/* Position content on top of the overlay */
.auth-page > :deep(div),
.auth-page > :deep(header),
.auth-page > :deep(footer) {
    position: relative;
    z-index: 2;
}


.auth-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  position: relative; /* Ensure it's on top of the overlay */
  z-index: 2;
}

.auth-slide {
  width: 55%;
  max-width: 650px;
  margin-right: 80px;
}

.auth-form {
  width: 45%;
  max-width: 420px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.title-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

h2 {
  font-size: 24px;
  color: #333;
  margin: 0;
}

.login-options {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.login-options span {
  cursor: pointer;
  color: #007BFF;
}

.login-options span:hover {
  text-decoration: underline;
}

.account-icon {
  width: 24px;
  height: 24px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 20px;
}

.input-container {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0 10px;
  background-color: white;
}

.input-container i {
  width: 20px;
  text-align: center;
  color: #999;
}

.input-field {
  flex: 1;
  height: 40px;
  border: none;
  outline: none;
  font-size: 14px;
  padding: 0 10px;
}

.captcha-group {
  display: flex;
  align-items: center;
}

.captcha-canvas {
  width: 100px;
  height: 40px;
  margin-right: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.captcha-input-field {
  flex: 1;
  margin-right: 10px;
}

.get-captcha-btn {
  white-space: nowrap;
  padding: 0 15px;
  height: 40px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.get-captcha-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

button {
  width: 100%;
  height: 40px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

button:hover {
  background-color: #0056b3;
}

.extra-options {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  font-size: 14px;
}

.extra-options a {
  color: #007BFF;
  text-decoration: none;
}

.extra-options a:hover {
  text-decoration: underline;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
}

.checkbox-label input {
  display: none;
}

.checkbox-custom {
  width: 16px;
  height: 16px;
  border: 1px solid #ddd;
  border-radius: 3px;
  margin-right: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.checkbox-label input:checked + .checkbox-custom {
  background-color: #007BFF;
  border-color: #007BFF;
}

.checkbox-label input:checked + .checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 12px;
}

.qrcode-container {
  text-align: center;
  margin-bottom: 20px;
}

.qrcode-img {
  width: 180px;
  height: 180px;
  margin: 20px auto;
  border: 1px solid #ddd;
  padding: 10px;
  background-color: white;
}

.qrcode-tips {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

.reset-options {
  display: flex;
  gap: 20px;
}

.reset-options button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 15px 0;
  background-color: white;
  border: 1px solid #ddd;
  color: #333;
}

.reset-options button:hover {
  background-color: #f5f5f5;
}

.reset-options button i {
  font-size: 24px;
  margin-bottom: 5px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
}

.modal-header button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  width: auto;
  height: auto;
  color: #333;
  margin: 0;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.terms-content, .privacy-content {
  line-height: 1.8;
  font-size: 14px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #ddd;
  text-align: right;
}

.modal-footer button {
  width: auto;
  padding: 0 20px;
}

@media (max-width: 768px) {
  .auth-content {
    flex-direction: column;
    padding: 20px;
  }
  
  .auth-slide, .auth-form {
    width: 100%;
    max-width: none;
    margin: 0;
  }
  
  .auth-slide {
    display: none;
  }
  
  .auth-form {
    margin-top: 20px;
  }
  
  .reset-options {
    flex-direction: column;
  }
  
  .modal-content {
    width: 90%;
  }
}

.link-style {
  cursor: pointer;
  color: #007BFF;
  font-size: 14px;
}

.link-style:hover {
  text-decoration: underline;
}
</style>  