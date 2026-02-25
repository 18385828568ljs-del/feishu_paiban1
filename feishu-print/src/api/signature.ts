import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface SignatureRequest {
  template_id?: number;
  record_id?: string;
  signer_name: string;
  signer_email?: string;
  document_title?: string;
  document_html?: string;
  expires_hours?: number;
}

export interface SignatureData {
  id: number;
  template_id?: number;
  record_id?: string;
  signer_name: string;
  signer_email?: string;
  document_title?: string;
  document_html?: string;
  signature_data?: string;
  signed_at?: string;
  status: 'pending' | 'signed' | 'expired';
  token: string;
  expires_at: string;
  created_at: string;
}

export const signatureApi = {
  create: async (data: SignatureRequest): Promise<SignatureData> => {
    const response = await axios.post(`${API_BASE}/api/signatures/`, data);
    return response.data;
  },

  getByToken: async (token: string): Promise<SignatureData> => {
    const response = await axios.get(`${API_BASE}/api/signatures/token/${token}`);
    return response.data;
  },

  submit: async (token: string, signatureData: string): Promise<SignatureData> => {
    const response = await axios.put(`${API_BASE}/api/signatures/token/${token}`, {
      signature_data: signatureData
    });
    return response.data;
  },

  getById: async (id: number): Promise<SignatureData> => {
    const response = await axios.get(`${API_BASE}/api/signatures/${id}`);
    return response.data;
  },

  getAll: async (): Promise<SignatureData[]> => {
    const response = await axios.get(`${API_BASE}/api/signatures/`);
    return response.data;
  },

  generateLink: (token: string): string => {
    const baseUrl = window.location.origin;
    const baseDir = import.meta.env.BASE_URL.replace(/\/$/, '');
    return `${baseUrl}${baseDir}/sign/${token}`;
  }
};
