直接把压缩包里的shape_predictor_68_face_landmarks.dat放到这里也行


# dlib 人脸关键点检测模型

眨眼检测功能需要下载 dlib 的 68 点人脸关键点检测模型文件。

## 下载步骤

1. 访问 dlib 官方模型下载页面或直接下载：
   ```
   http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   ```

2. 下载并解压缩后，将 `shape_predictor_68_face_landmarks.dat` 文件放置在此目录下

3. 文件放置正确后，目录结构应该是：
   ```
   SmartTransitMap/backend/models/
   └── shape_predictor_68_face_landmarks.dat
   ```

## 替代下载地址

如果官方地址下载较慢，可以尝试以下镜像地址：
- GitHub Release: https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2
- 百度网盘等云盘分享

## 注意事项

- 该文件大小约为 99MB
- 必须下载解压缩后的 `.dat` 文件，不是 `.bz2` 压缩文件
- 文件名必须完全匹配 `shape_predictor_68_face_landmarks.dat` 
