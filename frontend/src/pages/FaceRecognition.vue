<template>
  <div class="face-recognition-container">
    <!-- 左侧导航栏 -->
    <aside class="sidebar">
      <h2 class="sidebar-title">人脸识别模块</h2>
      <nav class="sidebar-nav">
        <ul>
          <li :class="{ active: currentTab === 'face-enter' }" @click="currentTab = 'face-enter'">人脸录入</li>
          <li :class="{ active: currentTab === 'face-verify' }" @click="currentTab = 'face-verify'">人脸验证</li>
          <li :class="{ active: currentTab === 'face-manage' }" @click="currentTab = 'face-manage'">人脸数据管理</li>
        </ul>
      </nav>
    </aside>
    <!-- 右侧内容区域 -->
    <main class="main-content">
      <section v-if="currentTab === 'face-enter'">
        <div class="enter-layout">
          <div class="left-column">
            <div class="panel">
              <div class="panel-header">摄像头</div>
              <div class="panel-body camera-panel-body">
                <div class="camera-feed">
                  <video ref="entryVideoPlayer" class="video-stream" autoplay playsinline></video>
                </div>
                <div class="snapshot-area">
                    <button class="btn" @click="takeSnapshot">拍照</button>
                    <div class="snapshot-preview">
                        <img v-if="snapshotDataUrl" :src="snapshotDataUrl" alt="快照">
                        <span v-else>拍照预览</span>
                    </div>
                </div>
              </div>
            </div>
          </div>
          <div class="right-column">
            <div class="panel">
              <div class="panel-header">录入</div>
              <div class="panel-body entry-form">
                <div class="feature-box">
                  <span>人脸特征</span>
                  <img v-if="snapshotDataUrl" :src="snapshotDataUrl" alt="人脸特征">
                  <img v-else :src="avatarImage" alt="人脸特征占位符">
                </div>
                <div class="input-group">
                  <label>姓名:</label>
                  <input type="text" v-model="entryName" />
                </div>
                <button class="btn" @click="saveEntry">保存</button>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section v-else-if="currentTab === 'face-verify'" class="verify-section">
        <div class="face-verify-box">
          <!-- Initial state before verification -->
          <template v-if="!isVerifying">
            <div class="face-placeholder">
              <img :src="avatarImage" alt="人脸示例" class="face-img">
            </div>
            <p>将面部放入识别框内</p>
            <button class="verify-btn" @click="startVerify">开始验证</button>
          </template>

          <!-- State during verification -->
          <template v-else>
            <h1>人脸验证</h1>
            <div class="face-placeholder">
              <video ref="videoPlayer" class="video-stream" autoplay playsinline></video>
            </div>
            <button class="btn" @click="captureVerify">识别</button>
            <p v-if="verifyResult">识别结果：{{ verifyResult }}</p>
          </template>
        </div>
      </section>
      <section v-else class="manage-section">
        <div class="panel">
          <div class="panel-header">人脸数据管理</div>
          <div class="panel-body manage-body">
            <ul>
              <li v-for="f in facesList" :key="f.name" class="face-item">
                <img :src="API_BASE + f.image" class="thumb" />
                <span>{{ f.name }}</span>
                <button class="btn btn-delete" @click="deleteFace(f.name)">删除</button>
              </li>
              <li v-if="!facesList.length">暂无数据</li>
            </ul>
          </div>
        </div>
      </section>
    </main>
    <canvas ref="snapshotCanvas" style="display: none;"></canvas>
    <div v-if="showUnknownModal" class="modal-overlay">
      <div class="modal-box">
        <h2>提示</h2>
        <p>您是非认证用户</p>
        <button class="btn" @click="closeUnknownModal">确认</button>
      </div>
    </div>
  </div>
</template>

<script>
import avatar from '@/assets/avatar.png';

export default {
  name: 'FaceRecognition',
  data() {
    return {
      currentTab: 'face-enter', // 默认显示人脸验证 tab，可根据需求调整
      avatarImage: avatar,
      isVerifying: false,
      verifyStream: null,
      entryStream: null,
      snapshotDataUrl: null,
      entryName: '',
      verifyResult: '',
      showUnknownModal: false,
      API_BASE: 'http://localhost:8000',
      facesList: [],
    }
  },
  watch: {
    currentTab(newTab, oldTab) {
      // Stop cameras when switching away from a tab
      if (oldTab === 'face-enter') {
        this.stopEntryCamera();
      }
      if (oldTab === 'face-verify') {
        this.stopVerifyCamera();
        this.isVerifying = false;
      }

      // Start camera when switching to the entry tab
      if (newTab === 'face-enter') {
        this.$nextTick(() => this.startEntryCamera());
      }

      if (newTab === 'face-manage') {
        this.fetchFaces();
      }
    }
  },
  methods: {
    // --- Verification Tab Methods ---
    async startVerify() {
      this.isVerifying = true;
      this.$nextTick(() => {
        this.startVerifyCamera();
      });
    },
    async startVerifyCamera() {
      try {
        this.verifyStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        const videoPlayer = this.$refs.videoPlayer;
        if (videoPlayer) {
          videoPlayer.srcObject = this.verifyStream;
        }
      } catch (err) {
        console.error("无法访问摄像头: ", err);
        alert("无法访问摄像头，请检查设备和浏览器权限。");
        this.isVerifying = false;
      }
    },
    stopVerifyCamera() {
      if (this.verifyStream) {
        this.verifyStream.getTracks().forEach(track => track.stop());
        this.verifyStream = null;
      }
    },

    // --- Entry Tab Methods ---
    async startEntryCamera() {
       try {
        this.entryStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        const videoPlayer = this.$refs.entryVideoPlayer;
        if (videoPlayer) {
          videoPlayer.srcObject = this.entryStream;
        }
      } catch (err) {
        console.error("无法访问录入摄像头: ", err);
        alert("无法启动摄像头，请检查您的设备和浏览器权限。");
      }
    },
    stopEntryCamera() {
      if (this.entryStream) {
        this.entryStream.getTracks().forEach(track => track.stop());
        this.entryStream = null;
      }
    },
    takeSnapshot() {
      const video = this.$refs.entryVideoPlayer;
      const canvas = this.$refs.snapshotCanvas;
      if (!video || !this.entryStream) {
        alert("摄像头未就绪！");
        return;
      }
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      // Flip the image horizontally for a mirror effect before drawing
      context.translate(canvas.width, 0);
      context.scale(-1, 1);
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      // Reset transform
      context.setTransform(1, 0, 0, 1, 0, 0);
      this.snapshotDataUrl = canvas.toDataURL('image/png');
    },
    saveEntry() {
      if (!this.snapshotDataUrl || !this.entryName.trim()) {
        alert('请先拍照并输入姓名！');
        return;
      }
      fetch(`${this.API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: this.entryName, image: this.snapshotDataUrl })
      })
        .then(res => {
          if (!res.ok) throw new Error('录入失败');
          return res.json();
        })
        .then(() => {
          alert('录入成功！');
          // Reset form
          this.entryName = '';
          this.snapshotDataUrl = null;
        })
        .catch(err => {
          console.error(err);
          alert('录入失败，请检查后端日志');
        });
    },
    captureVerify() {
      const video = this.$refs.videoPlayer;
      const canvas = this.$refs.snapshotCanvas;
      if (!video || !this.verifyStream) {
        alert('摄像头未就绪！');
        return;
      }
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.translate(canvas.width, 0);
      ctx.scale(-1, 1);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      const dataUrl = canvas.toDataURL('image/png');

      fetch(`${this.API_BASE}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataUrl })
      })
        .then(res => res.json())
        .then(json => {
          if (json.result === 'unknown') {
            this.showUnknownModal = true;
          } else {
            this.verifyResult = json.result;
          }
        })
        .catch(err => {
          console.error(err);
          alert('识别失败');
        });
    },
    closeUnknownModal() {
      this.showUnknownModal = false;
      this.stopVerifyCamera();
      this.isVerifying = false;
      this.verifyResult = '';
    },
    fetchFaces() {
      fetch(`${this.API_BASE}/faces`)
        .then(r => r.json())
        .then(j => {
          this.facesList = j.faces || [];
        })
        .catch(console.error);
    },
    deleteFace(name) {
      if (!confirm(`确定要删除用户 "${name}" 吗？`)) {
        return;
      }
      fetch(`${this.API_BASE}/faces/${name}`, {
        method: 'DELETE',
      })
        .then(res => {
          if (!res.ok) throw new Error(`删除失败: ${res.statusText}`);
          return res.json();
        })
        .then(() => {
          alert('删除成功！');
          this.fetchFaces(); // 重新加载列表
        })
        .catch(err => {
          console.error(err);
          alert('删除失败，请查看后端日志。');
        });
    },
  },
  mounted() {
    if (this.currentTab === 'face-enter') {
      this.startEntryCamera();
    }
  },
  unmounted() {
    this.stopVerifyCamera();
    this.stopEntryCamera();
  }
}
</script>

<style scoped>
.face-recognition-container {
  display: flex;
  height: 100vh;
  font-family: Arial, sans-serif;
}
.sidebar {
  width: 200px;
  background-color: #0b2b40;
  color: #fff;
  padding: 20px;
}
.sidebar-title {
  margin-bottom: 20px;
  font-size: 18px;
}
.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-nav li {
  padding: 10px 0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.sidebar-nav li:hover {
  background-color: #081e2b;
}
.sidebar-nav li.active {
  background-color: #081e2b;
  font-weight: bold;
}
.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f4f7f9;
  height: calc(100vh - 40px);
}
.enter-layout {
  display: flex;
  gap: 20px;
}
.left-column {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.right-column {
  flex: 1;
}
.panel {
  border: 2px solid #0b2b40;
  background-color: #fff;
  display: flex;
  flex-direction: column;
}
.panel-header {
  background-color: #0b2b40;
  color: white;
  padding: 8px 12px;
  font-weight: bold;
}
.panel-body {
  padding: 20px;
  display: flex;
  flex-grow: 1;
  align-items: center;
  justify-content: center;
}
.camera-panel-body {
  flex-direction: column;
  gap: 20px;
}
.camera-feed img {
  max-width: 250px;
  height: auto;
  border: 1px solid #ddd;
}
.snapshot-area {
  display: flex;
  align-items: center;
  gap: 20px;
}
.snapshot-preview {
  border: 1px solid #ccc;
  padding: 5px;
  width: 162px;
  height: 124px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #888;
}
.snapshot-preview img {
  width: 150px;
  height: auto;
}
.entry-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  height: 100%;
}
.feature-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid #ccc;
  padding: 15px;
  gap: 10px;
}
.feature-box img {
  width: 150px;
}
.input-group {
  display: flex;
  align-items: center;
  gap: 5px;
}
.input-group input {
    border: 1px solid #ccc;
    padding: 5px;
}
.btn {
  background-color: #0b2b40;
  color: white;
  border: none;
  padding: 8px 25px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
}
.verify-section {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.face-verify-box {
  text-align: center;
}
.face-verify-box h1 {
  margin-bottom: 20px;
  font-size: 24px;
  color: #0b2b40;
}
.face-placeholder {
  width: 450px;
  height: 450px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 20px;
  border: 3px solid #0b2b40;
  background-color: #000;
}
.face-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); /* Mirror effect for a natural feel */
}
.verify-btn {
  background-color: #0b2b40;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}
.verify-btn:hover {
  background-color: #081e2b;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-box {
  background: #fff;
  padding: 40px 30px;
  border-radius: 8px;
  width: 380px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.modal-box h2 {
  margin-bottom: 20px;
}
.manage-section {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 20px;
}
.manage-section .panel {
  width: 60%;
  min-width: 500px;
}
.manage-body {
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
}
.manage-body ul {
  list-style: none;
  padding: 0;
  width: 100%;
}
.manage-body li {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
}
.face-item {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 18px;
  position: relative;
}
.btn-delete {
  position: absolute;
  right: 10px;
  padding: 5px 15px;
  font-size: 14px;
  background-color: #d9534f;
}
.btn-delete:hover {
  background-color: #c9302c;
}
.thumb {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ccc;
}
</style>