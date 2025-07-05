import axios from "axios";
import { API_URL } from "@providers/config";

export interface CompanyInfo {
  id: number;
  is_ho: boolean;
  mis_id: string | boolean;
  write_date: string;
  max_write_date?: string | null;
}

export interface Company {
  id: number;
  name: string;
  owner_id: number;
  info: CompanyInfo;
}

// Hàm nhận token trực tiếp thay vì getAccessToken
export const fetchCompanies = async (token?: string): Promise<Company[]> => {
  try {
    const res = await axios.get(`${API_URL}/api/companies/`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    return res.data as Company[];
  } catch {
    return [];
  }
};
