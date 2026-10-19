
-- ============================================================
-- 电商智能客服系统 - 完整数据库建表脚本（含优化表）
-- 数据库：customer_service
-- MySQL 版本：8.0+
-- 字符集：utf8mb4
-- 包含：原始 ER 图 8 张表 + 优化新增 2 张表
-- ============================================================

CREATE DATABASE IF NOT EXISTS customer_service
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE customer_service;

-- 按依赖顺序删除旧表
DROP TABLE IF EXISTS ticket_logs;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS conversation_ratings;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS knowledge;
DROP TABLE IF EXISTS intents;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS users;

-- ============================================================
-- 1. 用户表（原始表 + 优化字段）
-- 优化新增：password_hash、status、updated_at
-- ============================================================
CREATE TABLE users (
    `id`            BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户id',
    `username`      VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL        COMMENT '密码哈希（优化新增）',
    `email`         VARCHAR(100)                 COMMENT '邮箱',
    `phone`         VARCHAR(20)                  COMMENT '手机号',
    `user_type`     ENUM('normal','vip','admin') DEFAULT 'normal' COMMENT '用户类型',
    `avatar_url`    VARCHAR(500)                 COMMENT '头像URL',
    `is_active`     BOOLEAN DEFAULT TRUE         COMMENT '是否激活',
    `status`        TINYINT      DEFAULT 1       COMMENT '状态：1正常 0禁用（优化新增）',
    `created_at`    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP  COMMENT '创建时间',
    `updated_at`    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '优化新增',
    INDEX `idx_username` (`username`),
    INDEX `idx_phone` (`phone`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 2. 客服坐席表（原始表 + 优化字段）
-- 优化新增：email、status
-- ============================================================
CREATE TABLE agents (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(50)  NOT NULL COMMENT '客服姓名',
    email       VARCHAR(100)          COMMENT '邮箱（优化新增）',
    description VARCHAR(255)          COMMENT '描述',
    is_active   BOOLEAN      DEFAULT TRUE COMMENT '是否启用',
    status      ENUM('online','busy','offline') DEFAULT 'offline' COMMENT '在线状态（优化新增）',
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客服坐席表';

-- ============================================================
-- 3. 意图识别记录表（原始表 + 优化字段）
-- 优化新增：entities JSON 槽位
-- ============================================================
CREATE TABLE intents (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '意图ID',
    `intent_name` VARCHAR(100) NOT NULL COMMENT '意图名称',
    `intent_code` VARCHAR(50) NOT NULL UNIQUE COMMENT '意图编码',
    `confidence` DECIMAL(5,4) DEFAULT 0.0 COMMENT '置信度 0.0-1.0',
    `description` VARCHAR(255) COMMENT '意图描述',
    `handler_type` ENUM('rag', 'tool', 'transfer', 'fallback') NOT NULL COMMENT '处理类型',
    `handler_config` JSON COMMENT '处理配置',
    `sample_utterances` TEXT COMMENT '示例语料',
    `priority` INT DEFAULT 0 COMMENT '优先级',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_intent_code` (`intent_code`),
    INDEX `idx_handler_type` (`handler_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='意图识别记录表';

-- ============================================================
-- 4. 商品表（原始表 + 优化字段）
-- 优化新增：images、status、updated_at
-- ============================================================
CREATE TABLE products (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(200) NOT NULL COMMENT '商品名称',
    category    VARCHAR(50)           COMMENT '分类',
    price       DECIMAL(10,2) NOT NULL COMMENT '价格',
    description TEXT                  COMMENT '描述',
    stock       INT           DEFAULT 0 COMMENT '库存',
    images      JSON                  COMMENT '图片列表（优化新增）',
    status      ENUM('on_sale','off_sale') DEFAULT 'on_sale' COMMENT '状态（优化新增）',
    created_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '优化新增'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';

-- ============================================================
-- 5. 会话表（原始表 + 优化字段）
-- 优化新增：status 枚举扩展、updated_at
-- ============================================================
CREATE TABLE `sessions` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '会话ID',
    `session_id` VARCHAR(64) NOT NULL UNIQUE COMMENT '会话唯一标识',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `agent_id` BIGINT COMMENT '分配的Agent ID',
    `status` ENUM('active', 'waiting', 'transferred', 'closed') DEFAULT 'active' COMMENT '会话状态',
    `channel` VARCHAR(20) DEFAULT 'web' COMMENT '来源渠道',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `ended_at` DATETIME COMMENT '结束时间',
    `last_message_at` DATETIME COMMENT '最后消息时间',
    `message_count` INT DEFAULT 0 COMMENT '消息数量',
    `satisfaction_score` TINYINT COMMENT '满意度评分',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`agent_id`) REFERENCES `agents`(`id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';

-- ============================================================
-- 6. 订单表（原始表 + 优化字段）
-- 优化新增：shipping_address、updated_at
-- ============================================================
CREATE TABLE `orders` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    `order_no` VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `status` ENUM('pending', 'paid', 'shipped', 'delivered', 'completed', 'cancelled', 'refunding', 'refunded') DEFAULT 'pending' COMMENT '订单状态',
    `total_amount` DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    `pay_amount` DECIMAL(10,2) COMMENT '实付金额',
    `shipping_address` JSON COMMENT '收货地址',
    `receiver_name` VARCHAR(50) COMMENT '收货人',
    `receiver_phone` VARCHAR(20) COMMENT '联系电话',
    `tracking_no` VARCHAR(50) COMMENT '物流单号',
    `remark` TEXT COMMENT '订单备注',
    `paid_at` DATETIME COMMENT '支付时间',
    `shipped_at` DATETIME COMMENT '发货时间',
    `delivered_at` DATETIME COMMENT '收货时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_order_no` (`order_no`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ============================================================
-- 7. 订单明细表（优化新增表）
-- 作用：解决订单与商品的多对多关系
-- ============================================================
CREATE TABLE order_items (
    id         BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id   BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity   INT    NOT NULL COMMENT '数量',
    unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
    CONSTRAINT fk_order_items_order   FOREIGN KEY (order_id)   REFERENCES orders(id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单明细表（优化新增）';

-- ============================================================
-- 8. 消息表（原始表 + 优化字段）
-- 优化新增：metadata JSON
-- ============================================================
CREATE TABLE `messages` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '消息ID',
    `session_id` VARCHAR(64) NOT NULL COMMENT '会话唯一标识',
    `sender_type` ENUM('user', 'bot', 'agent') NOT NULL COMMENT '发送者类型',
    `sender_id` BIGINT COMMENT '发送者ID',
    `content` TEXT NOT NULL COMMENT '消息内容',
    `content_type` ENUM('text', 'image', 'voice', 'file', 'quick_reply') DEFAULT 'text' COMMENT '内容类型',
    `intent_id` BIGINT COMMENT '识别的意图ID',
    `intent_confidence` DECIMAL(5,4) COMMENT '意图置信度',
    `sentiment` ENUM('positive', 'neutral', 'negative') COMMENT '情感倾向',
    `sentiment_score` DECIMAL(3,2) COMMENT '情感得分',
    `is_human_transfer` BOOLEAN DEFAULT FALSE COMMENT '是否转人工',
    `is_generated` BOOLEAN DEFAULT FALSE COMMENT '是否AI生成',
    `metadata` JSON COMMENT '元数据',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`session_id`) REFERENCES `sessions`(`session_id`) ON DELETE CASCADE,
    FOREIGN KEY (`intent_id`) REFERENCES `intents`(`id`) ON DELETE SET NULL,
    INDEX idx_session_created (session_id, created_at),
    INDEX `idx_sender_type` (`sender_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- ============================================================
-- 9. 知识库表（原始表 + 优化改造）
-- 优化改造：去掉 embeddings 字段，改用 vector_id 关联 Milvus
-- ============================================================
CREATE TABLE `knowledge` (
    `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '知识ID',
    `category` VARCHAR(50) NOT NULL COMMENT '知识分类',
    `question` TEXT NOT NULL COMMENT '问题',
    `answer` TEXT NOT NULL COMMENT '答案',
    `keywords` VARCHAR(500) COMMENT '关键词',
    `vector_id` VARCHAR(100) COMMENT '向量数据库ID',
    `embedding_model` VARCHAR(50) DEFAULT 'text-embedding-ada-002' COMMENT '向量化模型',
    `hit_count` INT DEFAULT 0 COMMENT '命中次数',
    `satisfaction_rate` DECIMAL(5,2) COMMENT '满意度',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_category` (`category`),
    INDEX `idx_keywords` (`keywords`(255)),
    FULLTEXT `ft_question` (`question`, `keywords`) WITH PARSER ngram
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表';

-- ============================================================
-- 10. 会话评分表（优化新增表）
-- 作用：用户对会话进行 1-5 星评分和评价
-- ============================================================
CREATE TABLE conversation_ratings (
    id             BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id     VARCHAR(64) NOT NULL,
    rating_score   TINYINT     NOT NULL CHECK (rating_score BETWEEN 1 AND 5) COMMENT '评分 1-5',
    rating_comment TEXT                COMMENT '评价内容',
    rating_time    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ratings_session FOREIGN KEY (session_id) REFERENCES sessions(session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话评分表（优化新增）';

-- ============================================================
-- 11. 工单表
-- ============================================================
CREATE TABLE `tickets` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '工单ID',
  `ticket_no` VARCHAR(32) NOT NULL UNIQUE COMMENT '工单号',
  `session_id` VARCHAR(64) COMMENT '关联会话ID',
  `user_id` BIGINT NOT NULL COMMENT '用户ID',
  `order_id` BIGINT COMMENT '关联订单ID',
  `type` ENUM('complaint', 'refund', 'consult', 'suggestion', 'other') NOT NULL COMMENT '工单类型',
  `title` VARCHAR(200) NOT NULL COMMENT '工单标题',
  `content` TEXT NOT NULL COMMENT '工单内容',
  `status` ENUM('pending', 'processing', 'resolved', 'closed') DEFAULT 'pending' COMMENT '处理状态',
  `priority` ENUM('low', 'normal', 'high', 'urgent') DEFAULT 'normal' COMMENT '优先级',
  `assigned_to` BIGINT COMMENT '处理人',
  `resolution` TEXT COMMENT '处理结果',
  `resolved_at` DATETIME COMMENT '解决时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`assigned_to`) REFERENCES `agents`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`),
  INDEX `idx_ticket_no` (`ticket_no`),
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工单表';

-- ============================================================
-- 12. 工单处理日志表
-- ============================================================

CREATE TABLE ticket_logs (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    ticket_id     BIGINT      NOT NULL,
    operator_type ENUM('user','agent','system') NOT NULL COMMENT '操作方',
    operator_id   BIGINT               COMMENT '操作人ID，系统操作为空',
    action        VARCHAR(50) NOT NULL COMMENT '操作：创建/分配/回复/状态变更/关闭',
    content       TEXT                 COMMENT '操作内容',
    created_at    TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket_logs_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    INDEX idx_ticket_logs_ticket (ticket_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工单处理日志表';

-- ============================================================
-- 13. 模型配置表
-- ============================================================

CREATE TABLE IF NOT EXISTS model_configs (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID',
    name            VARCHAR(100) NOT NULL COMMENT '配置名称',
    provider        VARCHAR(50)  NOT NULL COMMENT '服务商：deepseek/openai/siliconflow',
    type            ENUM('chat','embedding') NOT NULL COMMENT '类型',
    model           VARCHAR(200) NOT NULL COMMENT '模型名称',
    base_url        VARCHAR(255) NOT NULL COMMENT '接口地址',
    api_key         VARCHAR(500) NOT NULL COMMENT 'API Key',
    temperature     DECIMAL(3,2) DEFAULT 0.70 COMMENT '温度',
    max_tokens      INT DEFAULT 2048 COMMENT '最大token',
    is_default      BOOLEAN DEFAULT FALSE COMMENT '是否默认',
    status          ENUM('正常','异常') DEFAULT '正常' COMMENT '状态',
    description     VARCHAR(500) COMMENT '描述',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_type (type),
    INDEX idx_is_default (is_default)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型配置表';