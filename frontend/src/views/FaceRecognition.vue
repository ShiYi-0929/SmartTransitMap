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
                  <div class="camera-mask"></div>
                  <!-- 中心识别圆形框，仅视觉提示 -->
                  <div class="center-circle"></div>
                </div>
                <div class="snapshot-area">
                    <button class="btn" @click="takeSnapshot" :disabled="!isFaceInFrame">拍照</button>
                    <p v-if="!isFaceInFrame" style="color:#0b2b40;margin-top:8px;">请将人脸放置在拍摄范围内</p>
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
                  <label>ID:</label>
                  <input type="text" v-model="entryName" />
                </div>
                <button class="btn" @click="saveEntry" :disabled="isSaving || captureInProgress || snapshotImages.length < 3">
                  {{ isSaving ? '录入中...' : (captureInProgress ? '拍照中...' : '保存') }}
                </button>
                <p v-if="captureInProgress" style="color:#0b2b40;">拍照中，请稍后...</p>
                <p v-else-if="isSaving" style="color:#0b2b40;">录入中，请稍后...</p>
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
            <button class="btn" @click="captureVerify" :disabled="isRecognizing">
              {{ isRecognizing ? '识别中...' : '识别' }}
            </button>
            <p v-if="verifyResult">识别结果：{{ verifyResult }}</p>
          </template>
        </div>
      </section>
      <section v-else class="manage-section">
        <div class="panel">
          <div class="panel-header">人脸数据管理</div>
          <div class="panel-body manage-body">
            <div class="search-bar">
              <span class="search-icon">🔍</span>
              <input type="text" v-model="searchQuery" placeholder="点此搜索" />
              <span class="clear-icon" v-if="searchQuery" @click="clearSearch">×</span>
            </div>
            <ul>
              <li v-for="f in filteredFaces" :key="f.id" class="face-item">
                <img :src="API_BASE + f.image" class="thumb" @click="viewAlbum(f)" />
                <span>{{ f.id }}</span>
                <div class="actions">
                  <button class="btn btn-add" @click="addFace(f)">添加</button>
                  <button class="btn btn-edit" @click="openEditor(f)">编辑</button>
                  <button class="btn btn-delete" @click="askDeleteFace(f.id)">删除</button>
                </div>
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
    <!-- 人脸录入进行中提示 -->
    <div v-if="isSaving" class="modal-overlay">
      <div class="modal-box">
        <p style="font-size:18px;">人脸录入中，请稍后...</p>
      </div>
    </div>

    <div v-if="albumVisible" class="modal-overlay">
      <div class="modal-box album-box">
        <h2>人脸照片集</h2>
        <div class="album-grid">
          <img v-for="(img,idx) in albumImages" :key="idx" :src="API_BASE + img" />
          <p v-if="!albumImages.length">暂无记录</p>
        </div>
        <button class="btn" @click="closeAlbum">关闭</button>
      </div>
    </div>
    <!-- 编辑用户 -->
    <div v-if="editorVisible" class="modal-overlay">
      <div class="modal-box album-box" style="max-height:80vh;overflow:auto;">
        <h2>编辑用户</h2>
        <div class="input-group" style="margin-bottom:15px;">
          <label>ID:</label>
          <span>{{ editorName }}</span>
        </div>
        <div class="album-grid">
          <div v-for="(img,idx) in editorImages" :key="idx" style="position:relative;">
            <img :src="API_BASE + img" @click="openFullImage(img)" style="cursor:pointer;" />
            <span class="img-close" @click="confirmDeleteImage(img)">×</span>
          </div>
          <p v-if="!editorImages.length">暂无图片</p>
        </div>
        <button class="btn" @click="closeEditor">关闭</button>
      </div>
    </div>
    <!-- 删除图片确认弹窗 -->
    <div v-if="deleteModalVisible" class="modal-overlay">
      <div class="modal-box" style="width:320px;">
        <h2>确认删除</h2>
        <p style="margin-bottom:20px;">是否确认删除该照片？</p>
        <div style="display:flex;justify-content:center;gap:20px;">
          <button class="btn" @click="confirmDeleteImageReal">确定</button>
          <button class="btn btn-cancel" @click="cancelDeleteImage">取消</button>
        </div>
      </div>
    </div>
    <!-- 全屏查看 -->
    <div v-if="fullImageVisible" class="modal-overlay" @click="closeFullImage">
      <img :src="API_BASE + fullImageSrc" class="full-img" />
    </div>
    <!-- 自定义消息弹窗 -->
    <div v-if="msgModalVisible" class="modal-overlay">
      <div class="modal-box">
        <h2>提示</h2>
        <p>{{ msgModalText }}</p>
        <button class="btn" @click="closeMsgModal">确认</button>
      </div>
    </div>
    <!-- 删除用户确认弹窗 -->
    <div v-if="deleteFaceModalVisible" class="modal-overlay">
      <div class="modal-box" style="width:320px;">
        <h2>确认删除</h2>
        <p style="margin-bottom:20px;">是否确认删除该用户？</p>
        <div style="display:flex;justify-content:center;gap:20px;">
          <button class="btn" @click="confirmDeleteFaceReal">确定</button>
          <button class="btn btn-cancel" @click="cancelDeleteFace">取消</button>
        </div>
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
      snapshotImages: [],
      captureInProgress: false,
      entryName: '',
      editingId: null,
      editingOriginalName: '',
      verifyResult: '',
      showUnknownModal: false,
      msgModalVisible: false,
      msgModalText: '',
      isSaving: false,
      albumVisible: false,
      albumImages: [],
      editorVisible: false,
      editorPersonId: null,
      editorName: '',
      editorImages: [],
      nameSaving: false,
      isRecognizing: false, // 新增：用于禁用识别按钮
      API_BASE: 'http://localhost:8000',
      facesList: [],
      searchQuery: '',
      deleteModalVisible: false,
      pendingDeleteImage: '',
      fullImageVisible: false,
      fullImageSrc: '',
      faceDetected: false,
      isFaceInFrame: false, // 实时监测人脸是否在框内
      faceDetectionInterval: null, // 定时器
      deleteFaceModalVisible: false,
      pendingDeleteFaceId: '',
    }
  },
  computed: {
    filteredFaces() {
      const q = this.searchQuery.trim();
      if (!q) return this.facesList;
      return this.facesList.filter(f => f.name.includes(q));
    }
  },
  watch: {
    entryName(newVal) {
      if (this.editingId && newVal !== this.editingOriginalName) {
        // 用户修改了姓名，转为创建新用户
        this.editingId = null;
      }
    },
    currentTab(newTab, oldTab) {
      // Stop cameras when switching away from a tab
      if (oldTab === 'face-enter') {
        this.stopEntryCamera();
      }
      if (oldTab === 'face-verify') {
        this.stopVerifyCamera();
        this.isVerifying = false;
        this.verifyResult = ''; // 离开页面时清空结果
      }

      // Start camera when switching to the entry tab
      if (newTab === 'face-enter') {
        this.$nextTick(() => {
          this.startEntryCamera();
          this.startRealtimeFaceCheck();
        });
        // 每次进入录入页面，默认新建模式
        this.editingId = null;
        this.editingOriginalName = '';
      } else {
        this.stopRealtimeFaceCheck();
      }

      if (newTab === 'face-manage') {
        this.fetchFaces();
      }
    }
  },
  methods: {
    startRealtimeFaceCheck() {
      if (this.faceDetectionInterval) return; // 防止重复启动

      this.faceDetectionInterval = setInterval(async () => {
        const video = this.$refs.entryVideoPlayer;
        const canvas = this.$refs.snapshotCanvas;
        if (video && video.readyState >= 3 && canvas) {
          try {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            // 发送低质量jpg以提高性能
            const frame = canvas.toDataURL('image/jpeg', 0.5);

            const response = await fetch(`${this.API_BASE}/check_face_in_frame`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ image: frame })
            });

            if (!response.ok) throw new Error('Backend check failed');

            const result = await response.json();
            this.isFaceInFrame = result.in_frame;
            
            // 如果人脸移出范围，清除旧的快照预览
            if (!this.isFaceInFrame) {
              this.snapshotDataUrl = null;
            }

          } catch (error) {
            this.isFaceInFrame = false;
          }
        }
      }, 700); // 每 700ms 检测一次，降低请求频率
    },
    stopRealtimeFaceCheck() {
      if (this.faceDetectionInterval) {
        clearInterval(this.faceDetectionInterval);
        this.faceDetectionInterval = null;
      }
      this.isFaceInFrame = false;
    },
    // --- Verification Tab Methods ---
    async startVerify() {
      this.isVerifying = true;
      this.verifyResult = '';
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
    async takeSnapshot() {
      // 拍照时不再需要单独检查，因为按钮状态已经保证了人脸在框内
      const TOTAL = 3;
      const INTERVAL = 500; // ms

      this.captureInProgress = true;
      this.snapshotImages = [];

      const video = this.$refs.entryVideoPlayer;
      const canvas = this.$refs.snapshotCanvas;
      if (!video || !this.entryStream) {
        this.captureInProgress = false;
        return;
      }
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      
      const captureFrame = () => {
        ctx.translate(canvas.width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        ctx.setTransform(1, 0, 0, 1, 0, 0);

        // 裁剪中心 60% 区域，去除规定范围外的部分
        const cropLeft = Math.floor(canvas.width * 0.2);
        const cropTop = Math.floor(canvas.height * 0.2);
        const cropWidth = Math.floor(canvas.width * 0.6);
        const cropHeight = Math.floor(canvas.height * 0.6);

        const cropCanvas = document.createElement('canvas');
        cropCanvas.width = cropWidth;
        cropCanvas.height = cropHeight;
        const cropCtx = cropCanvas.getContext('2d');
        cropCtx.drawImage(canvas, cropLeft, cropTop, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);

        const dataUrl = cropCanvas.toDataURL('image/png');
        this.snapshotImages.push(dataUrl);
        if (this.snapshotImages.length === 1) {
          this.snapshotDataUrl = dataUrl;
        }
      };

      for (let i = 0; i < TOTAL; i++) {
        setTimeout(captureFrame, i * INTERVAL);
      }
      setTimeout(() => {
        this.captureInProgress = false;
      }, TOTAL * INTERVAL + 100);
    },
    saveEntry() {
      if (!this.snapshotDataUrl || !this.entryName.trim()) {
        this.showMsg('请先拍照并输入姓名！');
        return;
      }
      this.isSaving = true;
      fetch(`${this.API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: this.entryName, person_id: this.editingId || this.entryName.trim(), images: this.snapshotImages })
      })
        .then(res => {
          if (!res.ok) throw new Error('录入失败');
          return res.json();
        })
        .then(() => {
          this.showMsg('录入成功！');
          // Reset form
          this.entryName = '';
          this.snapshotDataUrl = null;
          this.snapshotImages = [];
          this.editingId = null;
          this.editingOriginalName = '';
        })
        .catch(err => {
          console.error(err);
          this.showMsg('录入失败，请检查后端日志');
        })
        .finally(() => {
          this.isSaving = false;
        });
    },
    captureVerify() {
      const video = this.$refs.videoPlayer;
      const canvas = this.$refs.snapshotCanvas;
      if (!video || !this.verifyStream) {
        this.showMsg('摄像头未就绪！');
        return;
      }
      this.isRecognizing = true; // 禁用按钮
      this.verifyResult = '';    // 清空上一次结果

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
            this.verifyResult = 'unknown';
            this.showUnknownModal = true;
          } else {
            this.verifyResult = json.result;
          }
        })
        .catch(err => {
          console.error(err);
          this.showMsg('识别失败');
        })
        .finally(() => {
          this.isRecognizing = false; // 无论成功失败，都恢复按钮
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
    deleteFace(personId) {
      fetch(`${this.API_BASE}/faces/${personId}`, {
        method: 'DELETE',
      })
        .then(res => {
          if (!res.ok) throw new Error(`删除失败: ${res.statusText}`);
          return res.json();
        })
        .then(() => {
          this.showMsg('删除成功！');
          this.fetchFaces(); // 重新加载列表
        })
        .catch(err => {
          console.error(err);
          this.showMsg('删除失败，请查看后端日志。');
        });
    },
    addFace(nameOrObj) {
      const isObj = typeof nameOrObj === 'object';
      const targetName = isObj ? nameOrObj.name : nameOrObj;
      const targetId = isObj ? nameOrObj.id : null;
      // 清除旧快照
      this.snapshotDataUrl = null;
      this.snapshotImages = [];
      // 自动填充姓名
      this.entryName = targetName;
      this.editingId = targetId;
      this.editingOriginalName = targetName; // 记录原始姓名
      // 跳转到录入 Tab
      this.currentTab = 'face-enter';
    },
    viewAlbum(personObj) {
      const id = typeof personObj === 'object' ? personObj.id : personObj;
      fetch(`${this.API_BASE}/faces/${id}/images`)
        .then(r => r.json())
        .then(j => {
          this.albumImages = j.images || [];
          this.albumVisible = true;
        })
        .catch(err => {
          console.error(err);
          this.showMsg('获取相册失败');
        });
    },
    closeAlbum() {
      this.albumVisible = false;
      this.albumImages = [];
    },
    openEditor(person) {
      this.editorPersonId = person.id;
      this.editorName = person.id; // 保持与列表一致
      this.nameSaving = false;
      // 获取图片列表
      fetch(`${this.API_BASE}/faces/${person.id}/images`)
        .then(r => r.json())
        .then(j => {
          this.editorImages = j.images || [];
          this.editorVisible = true;
        })
        .catch(err => {
          console.error(err);
          this.showMsg('获取图片失败');
        });
    },
    closeEditor() {
      this.editorVisible = false;
      this.editorPersonId = null;
      this.editorImages = [];
    },
    saveEditorName() {
      if (!this.editorPersonId) return;
      this.nameSaving = true;
      fetch(`${this.API_BASE}/faces/${this.editorPersonId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: this.editorName })
      })
        .then(r => r.json())
        .then(() => {
          // 更新管理列表显示
          this.fetchFaces();
          this.showMsg('ID 已更新');
        })
        .catch(err => {
          console.error(err);
          this.showMsg('更新失败');
        })
        .finally(() => {
          this.nameSaving = false;
        });
    },
    confirmDeleteImage(imgUrl) {
      this.pendingDeleteImage = imgUrl;
      this.deleteModalVisible = true;
    },
    cancelDeleteImage() {
      this.deleteModalVisible = false;
      this.pendingDeleteImage = '';
    },
    confirmDeleteImageReal() {
      if (!this.pendingDeleteImage) return;
      const filename = this.pendingDeleteImage.replace('/images/', '');
      fetch(`${this.API_BASE}/faces/${this.editorPersonId}/images/${filename}`, {
        method: 'DELETE'
      })
        .then(r => r.json())
        .then(() => {
          // 移除本地数组
          this.editorImages = this.editorImages.filter(i => i !== this.pendingDeleteImage);
          this.fetchFaces();
        })
        .catch(err => {
          console.error(err);
          this.showMsg('删除失败');
        })
        .finally(() => {
          this.deleteModalVisible = false;
          this.pendingDeleteImage = '';
        });
    },
    openFullImage(img) {
      this.fullImageSrc = img;
      this.fullImageVisible = true;
    },
    closeFullImage() {
      this.fullImageVisible = false;
      this.fullImageSrc = '';
    },
    clearSearch() {
      this.searchQuery = '';
    },
    showMsg(text) {
      this.msgModalText = text;
      this.msgModalVisible = true;
    },
    closeMsgModal() {
      this.msgModalVisible = false;
      this.msgModalText = '';
    },
    // ===== 用户删除弹窗相关 =====
    askDeleteFace(personId) {
      this.pendingDeleteFaceId = personId;
      this.deleteFaceModalVisible = true;
    },
    cancelDeleteFace() {
      this.deleteFaceModalVisible = false;
      this.pendingDeleteFaceId = '';
    },
    confirmDeleteFaceReal() {
      if (!this.pendingDeleteFaceId) return;
      this.deleteFace(this.pendingDeleteFaceId);
      this.deleteFaceModalVisible = false;
      this.pendingDeleteFaceId = '';
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
    this.stopRealtimeFaceCheck();
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
  align-items: stretch; /* 让左右列等高 */
}

.right-column .panel {
  height: 100%; /* 填满列高，底部与左侧对齐 */
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
.camera-feed {
  position: relative;
}

.center-circle {
   position: absolute;
   top: 50%;
   left: 50%;
  transform: translate(-50%, -50%) rotate(90deg);
  width: 60%; /* 更窄 */
  height: 50%; /* 更高 */
  border: none;
  border-radius: 50% / 40%;
  pointer-events: none;
  z-index: 2;
}

.camera-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4); /* 雾面 */
  pointer-events: none;
  z-index: 1;
  /* 通过 mask 制造中空椭圆 */
  -webkit-mask: radial-gradient(ellipse 30% 50% at 50% 50%, transparent 0%, transparent 60%, black 61%);
  mask: radial-gradient(ellipse 30% 50% at 50% 50%, transparent 0%, transparent 60%, black 61%);
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
  width: 220px;
  height: auto;
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
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
.album-box {
  max-width: 600px;
}
.album-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: center;
}
.album-grid img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border: 1px solid #ccc;
  border-radius: 4px;
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
}
.actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}
.btn-delete {
  padding: 5px 15px;
  font-size: 14px;
  background-color: #d9534f;
}
.btn-delete:hover {
  background-color: #c9302c;
}
.btn-add {
  background-color: #5cb85c;
  font-size: 14px;
  padding: 5px 15px;
}
.btn-add:hover {
  background-color: #4cae4c;
}
.thumb {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ccc;
}
.btn-edit {
  background-color: #0275d8;
  font-size: 14px;
  padding: 5px 15px;
  margin-left: 5px;
}
.btn-edit:hover {
  background-color: #025aa5;
}
.img-close {
  position:absolute;
  top:2px;
  right:4px;
  color:#fff;
  background:rgba(0,0,0,0.6);
  border-radius:50%;
  width:18px;
  height:18px;
  line-height:18px;
  text-align:center;
  cursor:pointer;
  font-weight:bold;
}
.btn-cancel {
  background-color: #aaa;
}
.btn-cancel:hover {
  background-color: #888;
}
.search-bar {
  position: relative;
  width: 100%;
  margin-bottom: 15px;
}
.search-bar input {
  width: 100%;
  padding: 10px 40px;
  border: none;
  border-radius: 30px;
  background-color: #e8f9ff;
  font-size: 16px;
  outline: none;
  box-sizing: border-box;
}
.search-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 18px;
  pointer-events: none;
}
.clear-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  font-size: 18px;
  cursor: pointer;
}
.full-img {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 8px;
}
</style>