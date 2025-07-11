import axios from 'axios';

export interface MrpProduction {
  // Khai báo các trường chính, có thể mở rộng thêm nếu cần
  id: number;
  name: string;
  state?: string;
  product_id?: any;
  product_qty?: number;
  product_uom_id?: any;
  date_start?: string;
  date_finished?: string;
  company_id?: any;
  user_id?: any;
  origin?: string;
  bom_id?: any;
  qty_produced?: number;
  qty_producing?: number;
  date_deadline?: string;
  create_date?: string;
  write_date?: string;
  create_uid?: any;
  write_uid?: any;
  warehouse_id?: any;
  workcenter_id?: any;
  production_location_id?: any;
  location_src_id?: any;
  location_dest_id?: any;
  priority?: string;
  sale_line_id?: any;
  picking_type_id?: any;
  picking_ids?: any;
  move_raw_ids?: any;
  move_finished_ids?: any;
  move_byproduct_ids?: any;
  components_availability?: string;
  components_availability_state?: string;
  consumption?: string;
  is_locked?: boolean;
  is_delayed?: boolean;
  is_outdated_bom?: boolean;
  is_planned?: boolean;
  production_capacity?: number;
  duration?: number;
  duration_expected?: number;
  extra_cost?: number;
  delay_alert_date?: string;
  delivery_count?: number;
  display_name?: string;
  forecasted_issue?: boolean;
  has_analytic_account?: boolean;
  has_message?: boolean;
  json_popover?: string;
  location_final_id?: any;
  lot_producing_id?: any;
  message_attachment_count?: number;
  message_follower_ids?: any;
  message_has_error?: boolean;
  message_has_error_counter?: number;
  message_has_sms_error?: boolean;
  message_ids?: any;
  message_is_follower?: boolean;
  message_needaction?: boolean;
  message_needaction_counter?: number;
  message_partner_ids?: any;
  mrp_production_backorder_count?: number;
  mrp_production_child_count?: number;
  mrp_production_source_count?: number;
  my_activity_date_deadline?: string;
  never_product_template_attribute_value_ids?: any;
  orderpoint_id?: any;
  procurement_group_id?: any;
  product_description_variants?: string;
  product_tmpl_id?: any;
  product_tracking?: string;
  product_uom_category_id?: any;
  product_uom_qty?: number;
  product_variant_attributes?: any;
  propagate_cancel?: boolean;
  purchase_order_count?: number;
  rating_ids?: any;
  reservation_state?: string;
  reserve_visible?: boolean;
  sale_order_count?: number;
  scrap_count?: number;
  scrap_ids?: any;
  search_date_category?: string;
  show_allocation?: boolean;
  show_final_lots?: boolean;
  show_lock?: boolean;
  show_lot_ids?: boolean;
  show_produce?: boolean;
  show_produce_all?: boolean;
  show_valuation?: boolean;
  unbuild_count?: number;
  unbuild_ids?: any;
  unreserve_visible?: boolean;
  use_create_components_lots?: boolean;
  valid_product_template_attribute_line_ids?: any;
  website_message_ids?: any;
  activity_ids?: any;
  activity_state?: string;
  activity_type_id?: any;
  activity_user_id?: any;
  activity_date_deadline?: string;
  activity_summary?: string;
  activity_type_icon?: string;
  activity_exception_icon?: string;
  activity_exception_decoration?: string;
  activity_calendar_event_id?: any;
  all_move_ids?: any;
  all_move_raw_ids?: any;
  allow_workorder_dependencies?: boolean;
  backorder_sequence?: number;
  finished_move_line_ids?: any;
  move_dest_ids?: any;
  workorders?: any; // chi tiết công đoạn nếu lấy detail
}

export async function getAllMrpProductions(token?: string): Promise<MrpProduction[]> {
  const baseUrl = 'http://localhost:8979';
  const res = await axios.get<MrpProduction[]>(
    `${baseUrl}/api/odoo/mrp_productions`,
    token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
  );
  return res.data;
}

export async function getMrpProductionDetail(id: number, token?: string): Promise<MrpProduction | null> {
  const baseUrl = 'http://localhost:8979';
  const res = await axios.get<MrpProduction | null>(
    `${baseUrl}/api/odoo/mrp_productions/${id}`,
    token ? { headers: { Authorization: `Bearer ${token}` } } : undefined
  );
  return res.data;
}
