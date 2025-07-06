// Export all API services from a single file
export { default as authApi } from './authApi';
export { default as studentApi } from './studentApi';
export { default as teacherApi } from './teacherApi';
export { default as summaryApi } from './summaryApi';
export { default as reportApi } from './reportApi';

// Export the axios client for direct use if needed
export { default as axiosClient } from './axiosClient';
