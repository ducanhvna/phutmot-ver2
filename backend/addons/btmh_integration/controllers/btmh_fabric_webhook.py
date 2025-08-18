# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class BTMHFabricWebhook(http.Controller):
    """Webhook controller to receive data from Microsoft Fabric"""
    
    @http.route('/btmh/fabric/webhook/sales', type='json', auth='none', methods=['POST'], csrf=False)
    def fabric_sales_webhook(self, **kwargs):
        """Receive sales data from Fabric dataflow"""
        try:
            data = request.get_json_data()
            
            if not data or not isinstance(data, list):
                return {
                    'status': 'error',
                    'message': 'Invalid data format. Expected list of sales records.'
                }
            
            # Process sales data
            sales_model = request.env['btmh.sales.data'].sudo()
            result = sales_model.fabric_webhook_sync(data)
            
            # Log the batch
            request.env['btmh.sync.log'].sudo().log_fabric_batch(
                batch_id=kwargs.get('batch_id', 'unknown'),
                records_processed=len(data),
                records_success=result.get('synced_records', 0),
                records_error=len(data) - result.get('synced_records', 0)
            )
            
            return result
            
        except Exception as e:
            _logger.error(f"Error processing Fabric sales webhook: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/btmh/fabric/webhook/payments', type='json', auth='none', methods=['POST'], csrf=False)
    def fabric_payments_webhook(self, **kwargs):
        """Receive payment data from Fabric dataflow"""
        try:
            data = request.get_json_data()
            
            if not data or not isinstance(data, list):
                return {
                    'status': 'error',
                    'message': 'Invalid data format. Expected list of payment records.'
                }
            
            # Process payment data
            payment_model = request.env['btmh.payment.data'].sudo()
            result = payment_model.fabric_webhook_sync(data)
            
            # Log the batch
            request.env['btmh.sync.log'].sudo().log_fabric_batch(
                batch_id=kwargs.get('batch_id', 'unknown'),
                records_processed=len(data),
                records_success=result.get('synced_records', 0),
                records_error=len(data) - result.get('synced_records', 0)
            )
            
            return result
            
        except Exception as e:
            _logger.error(f"Error processing Fabric payments webhook: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/btmh/fabric/webhook/deposits', type='json', auth='none', methods=['POST'], csrf=False)
    def fabric_deposits_webhook(self, **kwargs):
        """Receive deposit data from Fabric dataflow"""
        try:
            data = request.get_json_data()
            
            if not data or not isinstance(data, list):
                return {
                    'status': 'error',
                    'message': 'Invalid data format. Expected list of deposit records.'
                }
            
            # Process deposit data
            deposit_model = request.env['btmh.deposit.data'].sudo()
            result = deposit_model.fabric_webhook_sync(data)
            
            # Log the batch
            request.env['btmh.sync.log'].sudo().log_fabric_batch(
                batch_id=kwargs.get('batch_id', 'unknown'),
                records_processed=len(data),
                records_success=result.get('synced_records', 0),
                records_error=len(data) - result.get('synced_records', 0)
            )
            
            return result
            
        except Exception as e:
            _logger.error(f"Error processing Fabric deposits webhook: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/btmh/fabric/webhook/balance', type='json', auth='none', methods=['POST'], csrf=False)
    def fabric_balance_webhook(self, **kwargs):
        """Receive daily balance data from Fabric dataflow"""
        try:
            data = request.get_json_data()
            
            if not data or not isinstance(data, list):
                return {
                    'status': 'error',
                    'message': 'Invalid data format. Expected list of balance records.'
                }
            
            # Process balance data - can be stored in a separate model if needed
            # For now, we'll just log it
            request.env['btmh.sync.log'].sudo().log_fabric_batch(
                batch_id=kwargs.get('batch_id', 'unknown'),
                records_processed=len(data),
                records_success=len(data),
                records_error=0
            )
            
            return {
                'status': 'success',
                'message': f'Processed {len(data)} balance records'
            }
            
        except Exception as e:
            _logger.error(f"Error processing Fabric balance webhook: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    @http.route('/btmh/fabric/webhook/health', type='http', auth='none', methods=['GET'])
    def fabric_health_check(self):
        """Health check endpoint for Fabric to verify connectivity"""
        return json.dumps({
            'status': 'healthy',
            'service': 'BTMH-Odoo Integration',
            'timestamp': http.request.env.cr.now().isoformat()
        })
    
    @http.route('/btmh/sync/trigger/<string:model_name>', type='json', auth='user', methods=['POST'])
    def manual_sync_trigger(self, model_name, **kwargs):
        """Manual sync trigger for testing"""
        try:
            if model_name not in ['btmh.sales.data', 'btmh.payment.data', 'btmh.deposit.data']:
                return {
                    'status': 'error',
                    'message': f'Invalid model name: {model_name}'
                }
            
            model = request.env[model_name]
            pending_records = model.search([('sync_status', '=', 'pending')], limit=50)
            
            success_count = 0
            error_count = 0
            
            for record in pending_records:
                try:
                    record.action_sync_to_odoo()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    _logger.error(f"Error syncing {model_name} record {record.id}: {e}")
            
            return {
                'status': 'success',
                'processed': len(pending_records),
                'success': success_count,
                'errors': error_count
            }
            
        except Exception as e:
            _logger.error(f"Error in manual sync trigger: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
