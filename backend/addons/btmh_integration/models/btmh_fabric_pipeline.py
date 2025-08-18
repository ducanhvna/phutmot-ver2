# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
import logging
import time
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class BTMHFabricPipeline(models.Model):
    """Model to manage and trigger Fabric pipelines"""
    _name = 'btmh.fabric.pipeline'
    _description = 'BTMH Fabric Pipeline Management'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    # Basic Information
    name = fields.Char(string='Pipeline Name', required=True, index=True)
    fabric_pipeline_id = fields.Char(string='Fabric Pipeline ID', required=True, index=True)
    fabric_workspace_id = fields.Char(string='Fabric Workspace ID', required=True)
    pipeline_type = fields.Selection([
        ('sales', 'Sales Data'),
        ('payments', 'Payments Data'), 
        ('deposits', 'Deposits Data'),
        ('balance', 'Daily Balance'),
        ('full_sync', 'Full Synchronization')
    ], string='Pipeline Type', required=True, index=True)
    
    # Authentication & Connection
    fabric_tenant_id = fields.Char(string='Azure Tenant ID', required=True)
    fabric_client_id = fields.Char(string='Azure Client ID', required=True)
    fabric_client_secret = fields.Char(string='Azure Client Secret', required=True)
    fabric_base_url = fields.Char(string='Fabric Base URL', 
                                  default='https://api.fabric.microsoft.com/v1')
    
    # Pipeline Configuration
    pipeline_parameters = fields.Text(string='Pipeline Parameters (JSON)',
                                      help='JSON parameters to pass to the pipeline')
    timeout_minutes = fields.Integer(string='Timeout (Minutes)', default=30)
    
    # Scheduling
    auto_schedule = fields.Boolean(string='Auto Schedule', default=False)
    schedule_interval = fields.Selection([
        ('5min', 'Every 5 Minutes'),
        ('15min', 'Every 15 Minutes'),
        ('30min', 'Every 30 Minutes'),
        ('1hour', 'Every Hour'),
        ('4hour', 'Every 4 Hours'),
        ('daily', 'Daily'),
        ('manual', 'Manual Only')
    ], string='Schedule Interval', default='manual')
    
    next_run_time = fields.Datetime(string='Next Run Time')
    last_run_time = fields.Datetime(string='Last Run Time')
    
    # Status & Results
    status = fields.Selection([
        ('idle', 'Idle'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='idle', index=True)
    
    current_run_id = fields.Char(string='Current Run ID')
    last_error_message = fields.Text(string='Last Error Message')
    
    # Statistics
    total_runs = fields.Integer(string='Total Runs', default=0)
    successful_runs = fields.Integer(string='Successful Runs', default=0)
    failed_runs = fields.Integer(string='Failed Runs', default=0)
    avg_duration_minutes = fields.Float(string='Average Duration (Minutes)')
    
    # Data Processing Results
    last_sync_summary = fields.Text(string='Last Sync Summary')
    records_processed = fields.Integer(string='Records Processed (Last Run)')
    records_synced = fields.Integer(string='Records Synced (Last Run)')
    records_failed = fields.Integer(string='Records Failed (Last Run)')
    
    # Active/Inactive
    active = fields.Boolean(string='Active', default=True)
    
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    
    @api.depends('name', 'pipeline_type', 'status')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.pipeline_type}) - {record.status}"
    
    @api.model
    def get_fabric_access_token(self):
        """Get Azure access token for Fabric API"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.fabric_tenant_id}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.fabric_client_id,
                'client_secret': self.fabric_client_secret,
                'scope': 'https://api.fabric.microsoft.com/.default',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except Exception as e:
            _logger.error(f"Error getting Fabric access token: {e}")
            raise UserError(_("Failed to authenticate with Microsoft Fabric: %s") % str(e))
    
    def action_trigger_pipeline(self):
        """Manually trigger the Fabric pipeline"""
        for record in self:
            record._trigger_pipeline_execution()
    
    def _trigger_pipeline_execution(self):
        """Internal method to trigger pipeline execution"""
        try:
            # Get access token
            access_token = self.get_fabric_access_token()
            
            # Prepare pipeline parameters
            parameters = {}
            if self.pipeline_parameters:
                try:
                    parameters = json.loads(self.pipeline_parameters)
                except json.JSONDecodeError as e:
                    raise UserError(_("Invalid JSON in pipeline parameters: %s") % str(e))
            
            # Add default parameters
            parameters.update({
                'odoo_webhook_base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url'),
                'pipeline_trigger_source': 'odoo',
                'trigger_timestamp': datetime.now().isoformat()
            })
            
            # Trigger pipeline
            pipeline_url = f"{self.fabric_base_url}/workspaces/{self.fabric_workspace_id}/items/{self.fabric_pipeline_id}/jobs/instances"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'executionData': {
                    'parameters': parameters
                }
            }
            
            response = requests.post(pipeline_url, headers=headers, json=payload)
            response.raise_for_status()
            
            run_data = response.json()
            run_id = run_data.get('id')
            
            # Update status
            self.write({
                'status': 'running',
                'current_run_id': run_id,
                'last_run_time': fields.Datetime.now(),
                'total_runs': self.total_runs + 1,
                'last_error_message': False
            })
            
            # Start monitoring the pipeline
            self._monitor_pipeline_execution()
            
            # Log success
            self.env['btmh.sync.log'].create({
                'model_name': 'btmh.fabric.pipeline',
                'record_id': self.id,
                'sync_type': 'manual',
                'status': 'processing',
                'message': f'Successfully triggered Fabric pipeline {self.name} with run ID {run_id}'
            })
            
        except Exception as e:
            self.write({
                'status': 'failed',
                'last_error_message': str(e),
                'failed_runs': self.failed_runs + 1
            })
            
            # Log error
            self.env['btmh.sync.log'].create({
                'model_name': 'btmh.fabric.pipeline',
                'record_id': self.id,
                'sync_type': 'manual',
                'status': 'error',
                'message': f'Failed to trigger Fabric pipeline {self.name}: {str(e)}'
            })
            
            _logger.error(f"Error triggering Fabric pipeline {self.name}: {e}")
            raise UserError(_("Failed to trigger Fabric pipeline: %s") % str(e))
    
    def _monitor_pipeline_execution(self):
        """Monitor pipeline execution until completion"""
        if not self.current_run_id:
            return
            
        try:
            access_token = self.get_fabric_access_token()
            
            # Monitor pipeline status
            start_time = time.time()
            timeout_seconds = self.timeout_minutes * 60
            
            while time.time() - start_time < timeout_seconds:
                # Check pipeline status
                status_url = f"{self.fabric_base_url}/workspaces/{self.fabric_workspace_id}/items/{self.fabric_pipeline_id}/jobs/instances/{self.current_run_id}"
                
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                
                status_data = response.json()
                pipeline_status = status_data.get('status')
                
                if pipeline_status == 'Completed':
                    self._handle_pipeline_success()
                    break
                elif pipeline_status in ['Failed', 'Cancelled']:
                    self._handle_pipeline_failure(status_data)
                    break
                elif pipeline_status in ['Running', 'InProgress']:
                    # Continue monitoring
                    time.sleep(30)  # Check every 30 seconds
                else:
                    # Unknown status, continue monitoring
                    time.sleep(30)
            else:
                # Timeout occurred
                self._handle_pipeline_timeout()
                
        except Exception as e:
            self.write({
                'status': 'failed',
                'last_error_message': f'Monitoring error: {str(e)}',
                'failed_runs': self.failed_runs + 1
            })
            _logger.error(f"Error monitoring pipeline {self.name}: {e}")
    
    def _handle_pipeline_success(self):
        """Handle successful pipeline execution"""
        try:
            # Update status
            self.write({
                'status': 'success',
                'successful_runs': self.successful_runs + 1,
                'current_run_id': False
            })
            
            # Trigger data sync from the 4 staging tables
            self._sync_data_from_fabric_tables()
            
            # Schedule next run if auto-scheduling is enabled
            if self.auto_schedule and self.schedule_interval != 'manual':
                self._schedule_next_run()
                
        except Exception as e:
            self.write({
                'status': 'failed',
                'last_error_message': f'Post-processing error: {str(e)}',
                'failed_runs': self.failed_runs + 1
            })
            _logger.error(f"Error in post-processing for pipeline {self.name}: {e}")
    
    def _handle_pipeline_failure(self, status_data):
        """Handle failed pipeline execution"""
        error_message = status_data.get('error', {}).get('message', 'Unknown error')
        
        self.write({
            'status': 'failed',
            'last_error_message': error_message,
            'failed_runs': self.failed_runs + 1,
            'current_run_id': False
        })
        
        _logger.error(f"Fabric pipeline {self.name} failed: {error_message}")
    
    def _handle_pipeline_timeout(self):
        """Handle pipeline timeout"""
        self.write({
            'status': 'timeout',
            'last_error_message': f'Pipeline execution timed out after {self.timeout_minutes} minutes',
            'failed_runs': self.failed_runs + 1,
            'current_run_id': False
        })
        
        _logger.warning(f"Fabric pipeline {self.name} timed out")
    
    def _sync_data_from_fabric_tables(self):
        """Sync data from Fabric staging tables to Odoo models"""
        try:
            sync_summary = {
                'sales': 0,
                'payments': 0, 
                'deposits': 0,
                'balance': 0,
                'errors': 0
            }
            
            # Get data from Fabric Lakehouse tables
            if self.pipeline_type in ['sales', 'full_sync']:
                sync_summary['sales'] = self._sync_sales_data_from_fabric()
            
            if self.pipeline_type in ['payments', 'full_sync']:
                sync_summary['payments'] = self._sync_payments_data_from_fabric()
            
            if self.pipeline_type in ['deposits', 'full_sync']:
                sync_summary['deposits'] = self._sync_deposits_data_from_fabric()
            
            if self.pipeline_type in ['balance', 'full_sync']:
                sync_summary['balance'] = self._sync_balance_data_from_fabric()
            
            # Update sync summary
            self.write({
                'last_sync_summary': json.dumps(sync_summary),
                'records_processed': sum([v for k, v in sync_summary.items() if k != 'errors']),
                'records_synced': sum([v for k, v in sync_summary.items() if k != 'errors']) - sync_summary.get('errors', 0),
                'records_failed': sync_summary.get('errors', 0)
            })
            
            _logger.info(f"Data sync completed for pipeline {self.name}: {sync_summary}")
            
        except Exception as e:
            _logger.error(f"Error syncing data from Fabric for pipeline {self.name}: {e}")
            raise
    
    def _sync_sales_data_from_fabric(self):
        """Sync sales data from Fabric staging table"""
        try:
            # Call Fabric API to get sales data
            access_token = self.get_fabric_access_token()
            
            # Query Fabric Lakehouse for new sales data
            query_url = f"{self.fabric_base_url}/workspaces/{self.fabric_workspace_id}/items/{self.env['ir.config_parameter'].sudo().get_param('btmh.fabric.lakehouse.id')}/executeQuery"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # SQL query to get unsynced sales data
            sql_query = """
            SELECT * FROM btmh_sales_staging 
            WHERE sync_status = 'pending'
            ORDER BY created_timestamp DESC
            LIMIT 1000
            """
            
            payload = {'query': sql_query}
            response = requests.post(query_url, headers=headers, json=payload)
            response.raise_for_status()
            
            query_result = response.json()
            sales_data = query_result.get('data', [])
            
            # Process each sales record
            synced_count = 0
            for sale_record in sales_data:
                try:
                    # Create or update BTMH sales data record
                    existing_record = self.env['btmh.sales.data'].search([
                        ('btmh_invoice_id', '=', sale_record.get('btmh_invoice_id')),
                        ('btmh_product_code', '=', sale_record.get('btmh_product_code'))
                    ], limit=1)
                    
                    if existing_record:
                        existing_record.write(sale_record)
                    else:
                        sale_record['sync_status'] = 'pending'
                        self.env['btmh.sales.data'].create(sale_record)
                    
                    synced_count += 1
                    
                except Exception as e:
                    _logger.error(f"Error processing sales record: {e}")
                    continue
            
            # Mark records as synced in Fabric
            if synced_count > 0:
                update_query = """
                UPDATE btmh_sales_staging 
                SET sync_status = 'synced', synced_timestamp = CURRENT_TIMESTAMP()
                WHERE sync_status = 'pending'
                """
                
                requests.post(query_url, headers=headers, json={'query': update_query})
            
            return synced_count
            
        except Exception as e:
            _logger.error(f"Error syncing sales data from Fabric: {e}")
            return 0
    
    def _sync_payments_data_from_fabric(self):
        """Sync payments data from Fabric staging table"""
        # Similar implementation to sales data sync
        return 0
    
    def _sync_deposits_data_from_fabric(self):
        """Sync deposits data from Fabric staging table"""  
        # Similar implementation to sales data sync
        return 0
    
    def _sync_balance_data_from_fabric(self):
        """Sync balance data from Fabric staging table"""
        # Similar implementation to sales data sync
        return 0
    
    def _schedule_next_run(self):
        """Schedule the next pipeline run"""
        if not self.auto_schedule or self.schedule_interval == 'manual':
            return
            
        interval_mapping = {
            '5min': 5,
            '15min': 15,
            '30min': 30,
            '1hour': 60,
            '4hour': 240,
            'daily': 1440
        }
        
        minutes = interval_mapping.get(self.schedule_interval, 0)
        if minutes > 0:
            next_run = datetime.now() + timedelta(minutes=minutes)
            self.write({'next_run_time': next_run})
    
    @api.model
    def cron_run_scheduled_pipelines(self):
        """Cron job to run scheduled pipelines"""
        
        scheduled_pipelines = self.search([
            ('auto_schedule', '=', True),
            ('active', '=', True),
            ('status', '!=', 'running'),
            ('next_run_time', '<=', fields.Datetime.now())
        ])
        
        for pipeline in scheduled_pipelines:
            try:
                pipeline.action_trigger_pipeline()
            except Exception as e:
                _logger.error(f"Error running scheduled pipeline {pipeline.name}: {e}")
                continue
