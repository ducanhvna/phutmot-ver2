# Sử dụng multi-stage build để tối ưu image
FROM node:22-alpine AS builder

WORKDIR /app

# Sao chép package.json và package-lock.json trước để cache layer cài đặt dependencies
COPY package.json ./
# COPY package-lock.json ./

# Cài dependencies bằng npm ci (nhanh và chuẩn cho production)
RUN npm ci --legacy-peer-deps

# Sao chép toàn bộ mã nguồn vào container
COPY . .

ARG NEXT_PUBLIC_API_BASE_URL
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# Build ứng dụng Next.js
RUN npm run build

# Production image, chỉ chứa build output và node_modules
FROM node:22-alpine AS runner
WORKDIR /app

# Sao chép node_modules và build output từ builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# Nếu có các file cấu hình khác cần thiết, copy thêm ở đây
# COPY --from=builder /app/next.config.mjs ./next.config.mjs

EXPOSE 3000

CMD ["npm", "start"]
