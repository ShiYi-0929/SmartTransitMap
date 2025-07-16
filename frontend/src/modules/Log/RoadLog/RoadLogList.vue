<template>
  <div class="defect-list-container">
    <div class="filters">
      <input v-model="filters.id" placeholder="筛选编号" />
      <input v-model="filters.type" placeholder="筛选病害类型" />
      <select v-model="filters.severity">
        <option value="">所有严重程度</option>
        <option value="高">高</option>
        <option value="中">中</option>
        <option value="低">低</option>
        <option value="严重">严重</option>
      </select>
      <select v-model="filters.status">
        <option value="">所有状态</option>
        <option value="待处理">待处理</option>
        <option value="处理中">处理中</option>
        <option value="已完成">已完成</option>
      </select>
      <button @click="applyFilters">应用筛选</button>
      <button @click="resetFilters">重置筛选</button>
    </div>

    <div class="header">
      <div class="header-item">编号</div>
      <div class="header-item">病害照片</div>
      <div class="header-item">病害类型</div>
      <div class="header-item">严重程度</div>
      <div class="header-item">面积</div>
      <div class="header-item">置信位</div>
      <div class="header-item">状态</div>
      <div class="header-item">检测时间</div>
      <div class="header-item">操作</div>
    </div>

    <div v-for="defect in filteredDefects" :key="defect.id" class="defect-item">
      <div class="item-cell">{{ defect.id }}</div>
      <div class="item-cell defect-image">
        <img :src="defect.imageUrl" alt="病害照片" v-if="defect.imageUrl" />
        <span v-else>无照片</span>
      </div>
      <div class="item-cell">{{ defect.type }}</div>
      <div class="item-cell severity" :class="getSeverityClass(defect.severity)">
        {{ defect.severity }}
      </div>
      <div class="item-cell">{{ defect.area }} m²</div>
      <div class="item-cell">{{ defect.confidence }}%</div>
      <div class="item-cell status" :class="getStatusClass(defect.status)">
        {{ defect.status }}
      </div>
      <div class="item-cell">{{ defect.detectionTime }}</div>
      <div class="item-cell actions">
        <button @click="editDefect(defect)">编辑</button>
        <button @click="deleteDefect(defect.id)">删除</button>
      </div>
    </div>

    <div v-if="filteredDefects.length === 0" class="no-data">
      没有符合条件的病害信息。
    </div>

    <div class="bottom-actions">
      <button @click="addNewDefect" class="add-new-button">新增病害</button>
      <button @click="handleGoBack" class="back-button">返回</button>
    </div>

    <div v-if="showDefectModal" class="modal-overlay">
      <div class="modal-content">
        <h2>{{ editingDefect ? '编辑病害信息' : '新增病害信息' }}</h2>
        <form @submit.prevent="saveDefect">
          <div class="form-group">
            <label for="modalId">编号:</label>
            <input id="modalId" v-model="currentDefect.id" required />
          </div>
          <div class="form-group">
            <label for="modalImageUrl">照片URL:</label>
            <input id="modalImageUrl" v-model="currentDefect.imageUrl" />
          </div>
          <div class="form-group">
            <label for="modalType">病害类型:</label>
            <input id="modalType" v-model="currentDefect.type" required />
          </div>
          <div class="form-group">
            <label for="modalSeverity">严重程度:</label>
            <select id="modalSeverity" v-model="currentDefect.severity" required>
              <option value="高">高</option>
              <option value="中">中</option>
              <option value="低">低</option>
              <option value="严重">严重</option>
            </select>
          </div>
          <div class="form-group">
            <label for="modalArea">面积 (m²):</label>
            <input id="modalArea" type="number" step="0.1" v-model.number="currentDefect.area" required />
          </div>
          <div class="form-group">
            <label for="modalConfidence">置信位 (%):</label>
            <input id="modalConfidence" type="number" step="0.1" v-model.number="currentDefect.confidence" required />
          </div>
          <div class="form-group">
            <label for="modalStatus">状态:</label>
            <select id="modalStatus" v-model="currentDefect.status" required>
              <option value="待处理">待处理</option>
              <option value="处理中">处理中</option>
              <option value="已完成">已完成</option>
            </select>
          </div>
          <div class="form-group">
            <label for="modalDetectionTime">检测时间:</label>
            <input id="modalDetectionTime" type="text" v-model="currentDefect.detectionTime" placeholder="HH:MM:SS" required />
          </div>
          <div class="modal-actions">
            <button type="submit">{{ editingDefect ? '保存' : '添加' }}</button>
            <button type="button" @click="closeDefectModal">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DefectList',
  emits: ['close-road-log-list'], // 声明组件可以触发的事件
  data() {
    return {
      defects: [], // 初始化为空数组，将由 API 填充
      filters: {
        id: '',
        type: '',
        severity: '',
        status: '',
      },
      showDefectModal: false,
      editingDefect: null, // 存储正在编辑的病害
      currentDefect: { // 模态框中表单的模型
        id: '',
        imageUrl: '',
        type: '',
        severity: '高',
        area: 0,
        confidence: 0,
        status: '待处理',
        detectionTime: '',
      },
    };
  },
  computed: {
    filteredDefects() {
      return this.defects.filter(defect => {
        const matchesId = this.filters.id ? defect.id.includes(this.filters.id) : true;
        const matchesType = this.filters.type ? defect.type.includes(this.filters.type) : true;
        const matchesSeverity = this.filters.severity ? defect.severity === this.filters.severity : true;
        const matchesStatus = this.filters.status ? defect.status === this.filters.status : true;
        return matchesId && matchesType && matchesSeverity && matchesStatus;
      });
    },
  },
  methods: {
    getSeverityClass(severity) {
      switch (severity) {
        case '高':
          return 'severity-high';
        case '中':
          return 'severity-medium';
        case '低':
          return 'severity-low';
        case '严重':
          return 'severity-critical';
        default:
          return '';
      }
    },
    getStatusClass(status) {
      switch (status) {
        case '待处理':
          return 'status-pending';
        case '处理中':
          return 'status-in-progress';
        case '已完成':
          return 'status-completed';
        default:
          return '';
      }
    },
    applyFilters() {
      console.log('应用筛选:', this.filters);
    },
    resetFilters() {
      this.filters = {
        id: '',
        type: '',
        severity: '',
        status: '',
      };
    },
    addNewDefect() {
      this.editingDefect = null;
      this.currentDefect = {
        id: '',
        imageUrl: '',
        type: '',
        severity: '高',
        area: 0,
        confidence: 0,
        status: '待处理',
        detectionTime: '',
      };
      this.showDefectModal = true;
    },
    editDefect(defect) {
      this.editingDefect = defect;
      this.currentDefect = { ...defect };
      this.showDefectModal = true;
    },
    saveDefect() {
      if (this.editingDefect) {
        const index = this.defects.findIndex(d => d.id === this.editingDefect.id);
        if (index !== -1) {
          this.$set(this.defects, index, { ...this.currentDefect });
        }
      } else {
        if (!this.currentDefect.id) {
            this.currentDefect.id = `D${this.defects.length + 1}`;
        }
        this.defects.push({ ...this.currentDefect });
      }
      this.closeDefectModal();
    },
    deleteDefect(id) {
      if (confirm(`确定要删除编号为 ${id} 的病害信息吗？`)) {
        this.defects = this.defects.filter(defect => defect.id !== id);
      }
    },
    closeDefectModal() {
      this.showDefectModal = false;
      this.editingDefect = null;
    },
    handleGoBack() {
      this.$emit('close-road-log-list');
    },

    async fetchDefectsFromApi() {
      try {
        const response = await fetch('YOUR_API_ENDPOINT_HERE');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        this.defects = data;
      } catch (error) {
        console.error("获取病害数据失败:", error);
        // 如果 API 调用失败，加载模拟数据
        this.defects = [
          {
            id: '1',
            imageUrl: 'https://via.placeholder.com/60x60?text=Defect1',
            type: '纵向裂缝',
            severity: '高',
            area: 15.2,
            confidence: 89.0,
            status: '待处理',
            detectionTime: '14:30:15',
          },
          {
            id: '2',
            imageUrl: 'https://via.placeholder.com/60x60?text=Defect2',
            type: '坑洼',
            severity: '严重',
            area: 8.5,
            confidence: 95.0,
            status: '处理中',
            detectionTime: '14:15:22',
          },
          {
            id: '3',
            imageUrl: 'https://via.placeholder.com/60x60?text=Defect3',
            type: '横向裂缝',
            severity: '中',
            area: 22.1,
            confidence: 82.0,
            status: '已完成',
            detectionTime: '13:45:10',
          },
          {
            id: '4',
            imageUrl: 'https://via.placeholder.com/60x60?text=Defect4',
            type: '龟裂',
            severity: '高',
            area: 35.8,
            confidence: 91.0,
            status: '待处理',
            detectionTime: '13:20:33',
          },
          {
            id: '5',
            imageUrl: 'https://via.placeholder.com/60x60?text=Defect5',
            type: '纵向裂缝',
            severity: '低',
            area: 6.3,
            confidence: 76.0,
            status: '已完成',
            detectionTime: '12:55:44',
          },
          {
            id: '6',
            imageUrl: 'https://via.placeholder.com/60x60?text=Defect6',
            type: '坑洼',
            severity: '严重',
            area: 12.7,
            confidence: 93.0,
            status: '待处理',
            detectionTime: '12:30:18',
          },
        ];
      }
    },
  },
  mounted() {
    this.fetchDefectsFromApi(); // 组件挂载时调用 API
  }
};
</script>

<style scoped>
/* 保持原有的样式 */
.defect-list-container {
  font-family: Arial, sans-serif;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header, .defect-item {
  display: grid;
  grid-template-columns: 0.5fr 1fr 1.5fr 1fr 1fr 1fr 1fr 1.5fr 1.5fr;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.header {
  font-weight: bold;
  background-color: #eef;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  padding-left: 10px;
  padding-right: 10px;
}

.header-item, .item-cell {
  padding: 8px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.defect-item:nth-child(even) {
  background-color: #f6f6f6;
}

.defect-item:hover {
  background-color: #e0eaff;
}

.defect-image img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.severity-high, .severity-critical {
  color: white;
  background-color: #ff4d4f;
  padding: 4px 8px;
  border-radius: 4px;
}

.severity-medium {
  color: #c99300;
  background-color: #ffe58f;
  padding: 4px 8px;
  border-radius: 4px;
}

.severity-low {
  color: #52c41a;
  background-color: #f6ffed;
  padding: 4px 8px;
  border-radius: 4px;
}

.status-pending {
  color: #faad14;
  background-color: #fffbe6;
  padding: 4px 8px;
  border-radius: 4px;
}

.status-in-progress {
  color: #1890ff;
  background-color: #e6f7ff;
  padding: 4px 8px;
  border-radius: 4px;
}

.status-completed {
  color: #52c41a;
  background-color: #f6ffed;
  padding: 4px 8px;
  border-radius: 4px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  flex-wrap: wrap;
}

.filters input,
.filters select,
.filters button {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.filters button {
  background-color: #1890ff;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.filters button:hover {
  background-color: #40a9ff;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #888;
}

.bottom-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.add-new-button, .back-button {
  width: fit-content;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.add-new-button {
  background-color: #52c41a;
  color: white;
}

.add-new-button:hover {
  background-color: #73d13d;
}

.back-button {
  background-color: #607d8b; /* Example color for a back button */
  color: white;
}

.back-button:hover {
  background-color: #78909c;
}

/* Modal Styles */
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

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  width: 500px;
  max-width: 90%;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group select {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.modal-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.modal-actions button[type="submit"] {
  background-color: #1890ff;
  color: white;
}

.modal-actions button[type="submit"]:hover {
  background-color: #40a9ff;
}

.modal-actions button[type="button"] {
  background-color: #f0f0f0;
  color: #333;
}

.modal-actions button[type="button"]:hover {
  background-color: #e0e0e0;
}
</style>