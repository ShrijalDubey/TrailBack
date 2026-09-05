import axios from 'axios';
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const client = axios.create({ baseURL: API_URL, timeout: 15000, headers: { 'Content-Type':'application/json' } });
client.interceptors.request.use(config => { const key = localStorage.getItem('trailback_api_key'); if (key) config.headers['X-API-Key'] = key; return config; });
export const api = {
 health:()=>client.get('/health'), me:()=>client.get('/v1/me'),
 projects:()=>client.get('/projects'), project:(id)=>client.get(`/projects/${id}`), createProject:(body)=>client.post('/projects',body), updateProject:(id,body)=>client.patch(`/projects/${id}`,body), deleteProject:(id)=>client.delete(`/projects/${id}`),
 providers:()=>client.get('/providers'), models:()=>client.get('/models'), requests:(params={})=>client.get('/v1/requests',{params}), request:(id)=>client.get(`/v1/requests/${id}`),
 cost:()=>client.get('/v1/analytics/cost'), latency:()=>client.get('/v1/analytics/latency'),
 keys:(projectId)=>client.get('/v1/api-keys',{params:{project_id:projectId}}), createKey:(body)=>client.post('/v1/api-keys',body), revokeKey:(id)=>client.delete(`/v1/api-keys/${id}`),
 users:()=>client.get('/users'), createUser:(body)=>client.post('/users',body), updateUser:(id,body)=>client.patch(`/users/${id}`,body),
 chat:(body)=>client.post('/v1/chat/completions',body),
};
export default client;
