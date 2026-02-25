import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface Template {
  id: number;
  name: string;
  content: string;
  template_type?: string;  // 'normal' 或 'ai'
  is_system?: boolean;  // 是否为系统模版
  owner_id?: number | null; // 所有者ID
  created_at: string;
  updated_at?: string;
}

export interface TemplateCreate {
  name: string;
  content: string;
  template_type?: string;  // 'normal' 或 'ai'
}

export interface TemplateUpdate {
  name?: string;
  content?: string;
  template_type?: string;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 为这个 axios 实例添加请求拦截器，自动携带 session token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('session_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const templateApi = {
  // 获取所有模板
  getAll: async (search?: string, templateType?: string, owner?: string): Promise<Template[]> => {
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (templateType) params.template_type = templateType;
    if (owner) params.owner = owner;
    const response = await api.get<Template[]>('/api/templates/', { params });
    return response.data;
  },

  // 获取单个模板
  getById: async (id: number): Promise<Template> => {
    const response = await api.get<Template>(`/api/templates/${id}`);
    return response.data;
  },

  // 创建新模板
  create: async (template: TemplateCreate): Promise<Template> => {
    const response = await api.post<Template>('/api/templates/', template);
    return response.data;
  },

  // 更新模板
  update: async (id: number, template: TemplateUpdate): Promise<Template> => {
    const response = await api.put<Template>(`/api/templates/${id}`, template);
    return response.data;
  },

  // 删除模板
  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/templates/${id}`);
  },
};
