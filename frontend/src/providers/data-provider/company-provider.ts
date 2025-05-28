import axios from "axios";
import { API_URL } from "@providers/config";

export interface CompanyInfo {
  id: number;
  name: string;
  is_ho: boolean;
  mis_id: string | boolean;
  write_date: string;
}

export interface Company {
  id: number;
  db: string;
  url: string;
  username: string;
  password: string;
  company_code: string;
  company_name: string;
  info: {
    companies: CompanyInfo[];
  };
}

// Hàm nhận token trực tiếp thay vì getAccessToken
export const fetchCompanies = async (token?: string): Promise<CompanyInfo[]> => {
  try {
    const res = await axios.get(`${API_URL}/hrms/companies/`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    const json = res.data;
    if (json.results && json.results.length > 0) {
      return json.results[0].info.companies || [];
    }
    return [];
  } catch {
    return [];
  }
};
