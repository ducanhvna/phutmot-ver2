# Sử dụng Node.js 22 làm base image
FROM node:22-alpine 

# Thiết lập thư mục làm việc trong container
WORKDIR /app

RUN rm -rf node_modules package-lock.json

COPY src/ src/

# Sao chép package.json và package-lock.json trước để tối ưu cache
COPY package.json ./

# Xóa cache và cài đặt dependencies
RUN npm cache clean --force

RUN npm install recharts --force

# Cài đặt dependencies trước
RUN npm install --force
RUN npm install recharts --force

# Sao chép toàn bộ mã nguồn vào container
COPY . .
RUN ls -l src/components/  # Kiểm tra Grid.module.css

# Kiểm tra xem thư viện `chart.js` đã được cài chưa
# RUN npm run lint && npm run build
# Xây dựng ứng dụng Next.js
RUN npm run build

# Chạy ứng dụng trong chế độ production
CMD ["sh", "-c", "npm run build && npm start"]

