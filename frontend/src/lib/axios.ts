import axios from 'axios';

// Cấu hình mặc định cho axios
const instance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8979',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

export default instance;
