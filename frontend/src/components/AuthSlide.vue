<template>
  <div class="custom-slider">
    <div class="slides-container">
      <div 
        v-for="(image, index) in images" 
        :key="index" 
        :class="['slide', { active: currentIndex === index }]"
      >
        <img :src="image" alt="轮播图片" class="slide-img">
      </div>
    </div>
    <!-- 指示器 -->
    <div class="indicators">
      <span 
        v-for="(image, index) in images" 
        :key="index" 
        :class="{ active: currentIndex === index }"
        @click="goToSlide(index)"
      ></span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthSlide',
  props: {
    images: {
      type: Array,
      default: () => []
    },
    interval: {
      type: Number,
      default: 3000 // 默认3秒切换一次
    }
  },
  data() {
    return {
      currentIndex: 0,
      timer: null
    };
  },
  mounted() {
    this.startAutoSlide();
  },
  beforeUnmount() {
    this.stopAutoSlide(); // 替换beforeDestroy为beforeUnmount（Vue3兼容）
  },
  methods: {
    startAutoSlide() {
      this.timer = setInterval(() => {
        this.nextSlide();
      }, this.interval);
    },
    stopAutoSlide() {
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },
    nextSlide() {
      this.currentIndex = (this.currentIndex + 1) % this.images.length;
    },
    goToSlide(index) {
      this.currentIndex = index;
    }
  }
};
</script>

<style scoped>
.custom-slider {
  position: relative;
  width: 100%;
  height: 500px;
  overflow: hidden;
  border-radius: 8px;
}

.slides-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.8s ease-in-out;
}

.slide.active {
  opacity: 1;
  z-index: 1;
}

.slide-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.indicators {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.indicators span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.indicators span.active {
  background-color: white;
  transform: scale(1.2);
}
</style>