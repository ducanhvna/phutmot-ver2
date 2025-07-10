import axios from 'axios';

const API_BASE_URL = '/api/education'; // Điều chỉnh endpoint nếu backend khác

export interface Equipment {
  id: number;
  name: string;
  active?: boolean;
  serial_no?: string;
  category_id?: any;
  company_id?: any;
  department_id?: any;
  employee_id?: any;
  owner_user_id?: any;
  partner_id?: any;
  partner_ref?: string;
  technician_user_id?: any;
  warranty_date?: string;
  scrap_date?: string;
  note?: string;
  cost?: number;
  assign_date?: string;
  effective_date?: string;
  expected_mtbf?: number;
  mtbf?: number;
  mttr?: number;
  estimated_next_failure?: string;
  color?: number;
  display_name?: string;
  equipment_assign_to?: string;
  equipment_properties?: any;
  activity_state?: string;
  activity_type_id?: any;
  activity_user_id?: any;
  activity_date_deadline?: string;
  activity_summary?: string;
  activity_type_icon?: string;
  activity_exception_icon?: string;
  activity_exception_decoration?: string;
  activity_ids?: any;
  activity_calendar_event_id?: any;
  create_date?: string;
  create_uid?: any;
  write_date?: string;
  message_ids?: any;
  message_is_follower?: boolean;
  message_needaction?: boolean;
  message_needaction_counter?: number;
  message_partner_ids?: any;
  model?: string;
  my_activity_date_deadline?: string;
  rating_ids?: any;
  website_message_ids?: any;
  has_message?: boolean;
}

export async function getAllEquipments(): Promise<Equipment[]> {
  const res = await axios.get<Equipment[]>(`${API_BASE_URL}/equipments`);
  return res.data;
}