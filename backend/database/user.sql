/*
 Navicat Premium Dump SQL

 Source Server         : ymx
 Source Server Type    : MySQL
 Source Server Version : 80040 (8.0.40)
 Source Host           : localhost:3306
 Source Schema         : user

 Target Server Type    : MySQL
 Target Server Version : 80040 (8.0.40)
 File Encoding         : 65001

 Date: 14/07/2025 19:21:26
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for apply
-- ----------------------------
DROP TABLE IF EXISTS `apply`;
CREATE TABLE `apply`  (
  `applyID` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `userID` int UNSIGNED NOT NULL DEFAULT 1052,
  `username` varchar(255) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL DEFAULT '杨冕新',
  `result` int UNSIGNED NULL DEFAULT 0,
  PRIMARY KEY (`applyID`) USING BTREE,
  INDEX `username`(`username` ASC) USING BTREE,
  INDEX `userID`(`userID` ASC) USING BTREE,
  CONSTRAINT `userID` FOREIGN KEY (`userID`) REFERENCES `userinfo` (`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of apply
-- ----------------------------
INSERT INTO `apply` VALUES (1, 1052, '杨冕新', 2);
INSERT INTO `apply` VALUES (10, 1031, '赵艳利', 0);

-- ----------------------------
-- Table structure for systemlog
-- ----------------------------
DROP TABLE IF EXISTS `systemlog`;
CREATE TABLE `systemlog`  (
  `id` int UNSIGNED NOT NULL DEFAULT 1 AUTO_INCREMENT,
  `userID` int UNSIGNED NOT NULL DEFAULT 1052,
  `username` varchar(255) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL DEFAULT '杨冕新',
  `logtype` varchar(255) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL DEFAULT '普通操作',
  `description` varchar(255) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ymx`(`userID` ASC) USING BTREE,
  CONSTRAINT `ymx` FOREIGN KEY (`userID`) REFERENCES `userinfo` (`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of systemlog
-- ----------------------------
INSERT INTO `systemlog` VALUES (1, 1052, '杨冕新', '普通操作', '吃饭', '2025-07-14 19:17:24');
INSERT INTO `systemlog` VALUES (2, 1052, '杨冕新', '恶意操作', '吃饭不带我', '2025-07-14 19:20:34');
INSERT INTO `systemlog` VALUES (3, 1052, '杨冕新', '人脸不匹配', '乱刷脸', '2025-07-14 19:20:37');
INSERT INTO `systemlog` VALUES (4, 1052, '杨冕新', '活体检测不通过', '装死', '2025-07-14 19:20:59');

-- ----------------------------
-- Table structure for userinfo
-- ----------------------------
DROP TABLE IF EXISTS `userinfo`;
CREATE TABLE `userinfo`  (
  `username` varchar(255) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL DEFAULT '杨冕新',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '123456',
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '23301052@bjtu,edu.cn',
  `class` varchar(255) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL DEFAULT '普通用户',
  `userID` int UNSIGNED NOT NULL,
  PRIMARY KEY (`userID`) USING BTREE,
  INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of userinfo
-- ----------------------------
INSERT INTO `userinfo` VALUES ('赵艳利', '$2b$12$TORU/RhqWgwmOvrmzj8HFebGsGBr03mZykBZi/7IJswkKibDcE0FO', '2118286409@qq.com', '认证用户', 1031);
INSERT INTO `userinfo` VALUES ('杨冕新', '$2b$12$TORU/RhqWgwmOvrmzj8HFebGsGBr03mZykBZi/7IJswkKibDcE0FO', '23301052@bjtu.edu.cn', '认证用户', 1052);
INSERT INTO `userinfo` VALUES ('杨睿涵', '$2b$12$wrVLuA4TbytAef/OxfC.0u/nYt2eAheb7xUzZrAEedT97x.ZdW5dG', '23301053@bjtu.edu.cn', '管理员', 1053);
INSERT INTO `userinfo` VALUES ('岳雷铭', '$2b$12$TORU/RhqWgwmOvrmzj8HFebGsGBr03mZykBZi/7IJswkKibDcE0FO', '23301054@bjtu.edu.cn', '管理员', 1054);
INSERT INTO `userinfo` VALUES ('科比丶布莱恩特', '$2b$12$9Fl.5Z9BD3cZ9.BSeO0ElOw2yRPTLFe2AwZ9qNuCfYzIO5ewKkhaC', '2170725694@qq.com', '普通用户', 1145);

SET FOREIGN_KEY_CHECKS = 1;
