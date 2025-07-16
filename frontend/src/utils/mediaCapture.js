// frontend/src/utils/mediaCapture.js

let mediaRecorder;
let recordedChunks = [];

/**
 * 开始录制视频流。
 * @param {MediaStream} stream - 从摄像头获取的视频流。
 */
export const startRecording = (stream) => {
  if (!stream || !stream.active) {
    console.error("无法录制：视频流无效。");
    return;
  }
  // 使用更兼容的MIME类型，优先webm，其次mp4
  const options = {
    mimeType: MediaRecorder.isTypeSupported('video/webm; codecs=vp9')
              ? 'video/webm; codecs=vp9'
              : 'video/mp4'
  };
  recordedChunks = [];
  mediaRecorder = new MediaRecorder(stream, options);

  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      recordedChunks.push(event.data);
    }
  };

  mediaRecorder.start();
  console.log("录屏已开始。");
};

/**
 * 停止录制并返回视频Blob。
 * @returns {Promise<Blob|null>} 包含视频数据的Blob，如果录制失败则返回null。
 */
export const stopRecording = () => {
  return new Promise((resolve) => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.onstop = () => {
        const videoBlob = new Blob(recordedChunks, {
          type: mediaRecorder.mimeType,
        });
        recordedChunks = [];
        console.log("录屏已停止，返回Blob。");
        resolve(videoBlob);
      };
      mediaRecorder.stop();
    } else {
      console.log("录屏未在进行或已停止。");
      resolve(null);
    }
  });
};

/**
 * 从<video>元素或Canvas中截取一帧图像。
 * @param {HTMLVideoElement|HTMLCanvasElement} source - video或canvas元素。
 * @returns {Promise<string|null>} 包含JPEG图像数据的DataURL，如果源无效则返回null。
 */
export const takeScreenshot = (source) => {
    return new Promise((resolve) => {
        if (!source) {
            console.error("截图失败：源元素无效。");
            return resolve(null);
        }

        const canvas = document.createElement('canvas');
        // 保证截图尺寸与视频流尺寸一致
        canvas.width = source.videoWidth || source.width;
        canvas.height = source.videoHeight || source.height;
        const context = canvas.getContext('2d');
        context.drawImage(source, 0, 0, canvas.width, canvas.height);
        
        // 返回JPEG格式的DataURL，压缩质量为0.9，以减小体积
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        resolve(dataUrl);
        console.log("截图成功。");
    });
}; 

/**
 * 将 Base64 DataURL 转换为 Blob。
 * @param {string} dataURL - 形如 "data:image/png;base64,..." 的字符串。
 * @returns {Blob}
 */
export function dataURLToBlob(dataURL) {
  const parts = dataURL.split(',');
  const mimeMatch = parts[0].match(/:(.*?);/);
  const mime = mimeMatch ? mimeMatch[1] : 'application/octet-stream';
  const bstr = atob(parts[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new Blob([u8arr], { type: mime });
}

/**
 * 截取整个页面的截图。
 * @returns {Promise<string>} 包含页面截图的JPEG格式的DataURL。
 */
import html2canvas from 'html2canvas';

export async function capturePageScreenshot() {
  try {
    const canvas = await html2canvas(document.body, {
      useCORS: true, // 允许加载跨域图片
      logging: false, // 关闭在控制台的冗余日志
    });
    return canvas.toDataURL('image/jpeg', 0.85); // 返回JPEG以优化大小
  } catch (error) {
    console.error("整页截图失败:", error);
    return null;
  }
} 