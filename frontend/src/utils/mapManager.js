/**
 * 全局地图API管理器
 * 解决多组件同时加载地图API的冲突问题
 */

class MapAPIManager {
  constructor() {
    this.isLoading = false
    this.isLoaded = false
    this.loadPromise = null
    // 测试用的API key，生产环境请替换为正式的key
    this.apiKey = 'ac9b745946df9aee02cf0515319407df'
    this.maxRetries = 3
    this.retryCount = 0
  }

  /**
   * 加载高德地图API
   * @returns {Promise<AMap>}
   */
  async loadAPI() {
    // 如果已经加载完成，直接返回
    if (this.isLoaded && window.AMap) {
      console.log('高德地图API已加载，直接返回')
      return Promise.resolve(window.AMap)
    }

    // 如果正在加载，返回现有的Promise
    if (this.isLoading && this.loadPromise) {
      console.log('高德地图API正在加载中，等待现有加载完成')
      return this.loadPromise
    }

    // 开始新的加载过程
    console.log('开始加载高德地图API')
    this.isLoading = true
    
    this.loadPromise = this._loadAPIWithRetry()
    return this.loadPromise
  }

  /**
   * 带重试机制的API加载
   * @private
   */
  async _loadAPIWithRetry() {
    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        console.log(`高德地图API加载尝试 ${attempt + 1}/${this.maxRetries}`)
        return await this._loadAPISingle()
      } catch (error) {
        console.warn(`第 ${attempt + 1} 次加载失败:`, error.message)
        
        if (attempt === this.maxRetries - 1) {
          this.isLoading = false
          throw new Error(`高德地图API加载失败，已重试 ${this.maxRetries} 次`)
        }
        
        // 等待一段时间后重试
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)))
      }
    }
  }

  /**
   * 单次API加载
   * @private
   */
  _loadAPISingle() {
    return new Promise((resolve, reject) => {
      // 检查是否已经存在
      if (window.AMap) {
        this.isLoaded = true
        this.isLoading = false
        resolve(window.AMap)
        return
      }

      // 生成唯一的回调函数名
      const callbackName = `amapCallback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      
      // 创建script标签
      const script = document.createElement('script')
      script.type = 'text/javascript'
      script.async = true
      script.src = `https://webapi.amap.com/maps?v=2.0&key=${this.apiKey}&callback=${callbackName}`
      
      // 设置超时
      const timeout = setTimeout(() => {
        cleanup()
        reject(new Error('高德地图API加载超时'))
      }, 10000) // 10秒超时
      
      // 清理函数
      const cleanup = () => {
        clearTimeout(timeout)
        delete window[callbackName]
        if (script.parentNode) {
          document.head.removeChild(script)
        }
      }
      
      // 设置成功回调
      window[callbackName] = () => {
        this.isLoaded = true
        this.isLoading = false
        this.retryCount = 0
        console.log('✅ 高德地图API加载成功')
        cleanup()
        resolve(window.AMap)
      }
      
      // 设置错误回调
      script.onerror = () => {
        this.retryCount++
        cleanup()
        reject(new Error(`高德地图API网络请求失败 (尝试 ${this.retryCount})`))
      }
      
      document.head.appendChild(script)
    })
  }

  /**
   * 重置加载状态（用于错误恢复）
   */
  reset() {
    console.log('重置地图API管理器状态')
    this.isLoading = false
    this.loadPromise = null
    // 不重置 isLoaded，因为API已经加载成功
  }

  /**
   * 获取当前状态
   */
  getStatus() {
    return {
      isLoading: this.isLoading,
      isLoaded: this.isLoaded,
      hasAPI: !!window.AMap
    }
  }
}

// 创建单例实例
const mapAPIManager = new MapAPIManager()

export default mapAPIManager 