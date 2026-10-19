# ============================================================
# 前端 Dockerfile
# 多阶段构建：Node 构建 + Nginx 运行
# ============================================================

# ---------- 构建阶段 ----------
FROM node:22-alpine AS builder

WORKDIR /app

# 换 npm 国内源
RUN npm config set registry https://registry.npmmirror.com

# 复制依赖清单，利用缓存
COPY frontend/package*.json ./

# 装依赖
RUN npm ci

# 复制前端源码
COPY frontend .

# 构建生产包
RUN npm run build

# ---------- 运行阶段 ----------
FROM nginx:alpine

# 拷贝构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 拷贝 Nginx 配置
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]