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

 Date: 10/07/2025 10:43:20
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for apply
-- ----------------------------
DROP TABLE IF EXISTS `apply`;
CREATE TABLE `apply`  (
  `applyID` int UNSIGNED NOT NULL AUTO_INCREMENT,
  `userID` int UNSIGNED NOT NULL DEFAULT 1031,
  `username` varchar(255) CHARACTER SET gb2312 COLLATE gb2312_chinese_ci NOT NULL DEFAULT '杨冕新',
  `result` int UNSIGNED NULL DEFAULT 0,
  PRIMARY KEY (`applyID`) USING BTREE,
  INDEX `username`(`username` ASC) USING BTREE,
  INDEX `userID`(`userID` ASC) USING BTREE,
  CONSTRAINT `username` FOREIGN KEY (`username`) REFERENCES `userinfo` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `userID` FOREIGN KEY (`userID`) REFERENCES `userinfo` (`userID`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = gb2312 COLLATE = gb2312_chinese_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of apply
-- ----------------------------
INSERT INTO `apply` VALUES (1, 1031, '杨冕新', 0);

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
INSERT INTO `userinfo` VALUES ('赵艳利', '$2b$12$TORU/RhqWgwmOvrmzj8HFebGsGBr03mZykBZi/7IJswkKibDcE0FO', '2118286409@qq.com', '普通用户', 1031);
INSERT INTO `userinfo` VALUES ('杨冕新', '$2b$12$TORU/RhqWgwmOvrmzj8HFebGsGBr03mZykBZi/7IJswkKibDcE0FO', '23301052@bjtu.edu.cn', '认证用户', 1052);
INSERT INTO `userinfo` VALUES ('杨睿涵', '$2b$12$l1ZKUejbJsMVBPYNZRjc5Odq4wszJHHXiYQXOoeJN28uDRxY00/0O', '23301053@bjtu.edu.cn', '管理员', 1053);
INSERT INTO `userinfo` VALUES ('岳雷铭', '$2b$12$TORU/RhqWgwmOvrmzj8HFebGsGBr03mZykBZi/7IJswkKibDcE0FO', '23301054@bjtu.edu.cn', '管理员', 1054);
INSERT INTO `userinfo` VALUES ('科比丶布莱恩特', '$2b$12$9Fl.5Z9BD3cZ9.BSeO0ElOw2yRPTLFe2AwZ9qNuCfYzIO5ewKkhaC', '2170725694@qq.com', '普通用户', 1145);

SET FOREIGN_KEY_CHECKS = 1;
