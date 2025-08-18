# Microsoft Fabric Pipeline Configuration for BTMH-Odoo Integration

## Overview
This guide shows how to set up Microsoft Fabric pipelines that will be triggered by Odoo and sync data to staging tables in Fabric Lakehouse.

## Architecture Flow
```
BTMH POS (SQL Server) → Fabric Pipeline (Triggered by Odoo) → Lakehouse Staging Tables → Odoo Models
```

## 1. Setup Fabric Workspace & Service Principal

### Create Service Principal in Azure
```bash
# Using Azure CLI
az ad sp create-for-rbac --name "btmh-odoo-integration" --role contributor --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# Note down:
# - Application (client) ID
# - Directory (tenant) ID  
# - Client Secret
```

### Grant Fabric Permissions
1. Go to Fabric Admin Portal
2. Add Service Principal to Workspace with Admin role
3. Enable "Service principals can use Fabric APIs" in tenant settings

## 2. Create Fabric Data Pipeline Templates

### 2.1 Sales Data Pipeline

Create pipeline: `btmh-sales-data-pipeline`

#### Pipeline Activities:

**Activity 1: Get Parameters**
```json
{
    "name": "Get Pipeline Parameters",
    "type": "SetVariable", 
    "typeProperties": {
        "variableName": "BatchSize",
        "value": {
            "value": "@pipeline().parameters.batch_size",
            "type": "Expression"
        }
    }
}
```

**Activity 2: Extract Sales Data**
```json
{
    "name": "Extract BTMH Sales Data",
    "type": "Copy",
    "dependsOn": [{"activity": "Get Pipeline Parameters", "dependencyConditions": ["Succeeded"]}],
    "typeProperties": {
        "source": {
            "type": "SqlServerSource",
            "sqlReaderQuery": {
                "value": "SELECT TOP (@{variables('BatchSize')}) * FROM (\n    SELECT \n        SlBlM.Id as btmh_invoice_id,\n        SlBlM.StoreCode as store_code,\n        SlBlM.Status as status,\n        SlBlM.CustomerId as btmh_customer_id,\n        Customer.CustomerName as customer_name,\n        Customer.Phone as customer_phone,\n        SlBlD.ProductId as btmh_product_id,\n        Product.ProductCode as btmh_product_code,\n        Product.ProductName as product_name,\n        SlBlD.Quantity as quantity,\n        SlBlD.UnitPrice as unit_price,\n        SlBlD.TotalAmount as total_amount,\n        SlBlD.GoldWeight as gold_weight,\n        SlBlD.LaborCost as labor_cost,\n        SlBlD.StoneCost as stone_cost,\n        SlBlM.CreatedDate as created_date,\n        SlBlM.UpdatedDate as updated_date,\n        'pending' as sync_status,\n        CURRENT_TIMESTAMP as created_timestamp\n    FROM SlBlM \n    INNER JOIN SlBlD ON SlBlM.Id = SlBlD.SlBlMId\n    LEFT JOIN Customer ON SlBlM.CustomerId = Customer.Id\n    LEFT JOIN Product ON SlBlD.ProductId = Product.Id\n    WHERE SlBlM.Status IN ('Completed', 'Paid')\n        AND SlBlM.UpdatedDate >= DATEADD(hour, -1, GETDATE())\n) as recent_sales\nORDER BY created_date DESC",
                "type": "Expression"
            }
        },
        "sink": {
            "type": "LakehouseTableSink", 
            "tableActionSettings": {
                "loadOption": "OverwriteTable"
            }
        },
        "enableStaging": false
    },
    "inputs": [
        {
            "referenceName": "BTMH_SQL_Server_Dataset",
            "type": "DatasetReference"
        }
    ],
    "outputs": [
        {
            "referenceName": "Lakehouse_btmh_sales_staging",
            "type": "DatasetReference"
        }
    ]
}
```

**Activity 3: Notify Odoo Pipeline Complete**
```json
{
    "name": "Notify Odoo Completion",
    "type": "WebActivity",
    "dependsOn": [{"activity": "Extract BTMH Sales Data", "dependencyConditions": ["Succeeded"]}],
    "typeProperties": {
        "method": "POST",
        "url": {
            "value": "@concat(pipeline().parameters.odoo_webhook_base_url, '/btmh/fabric/pipeline/completed')",
            "type": "Expression"
        },
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_ODOO_API_TOKEN"
        },
        "body": {
            "pipeline_id": "@pipeline().RunId",
            "pipeline_name": "btmh-sales-data-pipeline", 
            "pipeline_type": "sales",
            "status": "completed",
            "records_processed": "@activity('Extract BTMH Sales Data').output.rowsCopied",
            "execution_time": "@utcnow()",
            "fabric_run_id": "@pipeline().RunId"
        }
    }
}
```

### 2.2 Parameters Configuration

Pipeline Parameters:
```json
{
    "batch_size": {
        "type": "int",
        "defaultValue": 1000
    },
    "odoo_webhook_base_url": {
        "type": "string", 
        "defaultValue": "https://your-odoo-instance.com"
    },
    "table_name": {
        "type": "string",
        "defaultValue": "btmh_sales_staging"
    }
}
```

## 3. Create Staging Tables in Lakehouse

### Sales Staging Table
```sql
CREATE TABLE btmh_sales_staging (
    btmh_invoice_id BIGINT,
    store_code VARCHAR(50),
    status VARCHAR(50),
    btmh_customer_id BIGINT,
    customer_name VARCHAR(255),
    customer_phone VARCHAR(50),
    btmh_product_id BIGINT,
    btmh_product_code VARCHAR(100),
    product_name VARCHAR(255),
    quantity DECIMAL(18,6),
    unit_price DECIMAL(18,6),
    total_amount DECIMAL(18,6),
    gold_weight DECIMAL(18,6),
    labor_cost DECIMAL(18,6),
    stone_cost DECIMAL(18,6),
    created_date DATETIME2,
    updated_date DATETIME2,
    sync_status VARCHAR(50) DEFAULT 'pending',
    created_timestamp DATETIME2 DEFAULT CURRENT_TIMESTAMP(),
    synced_timestamp DATETIME2,
    fabric_run_id VARCHAR(255)
);
```

### Payments Staging Table  
```sql
CREATE TABLE btmh_payments_staging (
    btmh_payment_id BIGINT,
    store_code VARCHAR(50),
    payment_type VARCHAR(10),
    reference_id BIGINT,
    amount DECIMAL(18,6),
    payment_method VARCHAR(50),
    payment_date DATETIME2,
    notes TEXT,
    sync_status VARCHAR(50) DEFAULT 'pending',
    created_timestamp DATETIME2 DEFAULT CURRENT_TIMESTAMP(),
    synced_timestamp DATETIME2,
    fabric_run_id VARCHAR(255)
);
```

### Deposits Staging Table
```sql
CREATE TABLE btmh_deposits_staging (
    btmh_deposit_id BIGINT,
    store_code VARCHAR(50),
    customer_id BIGINT,
    customer_name VARCHAR(255),
    deposit_amount DECIMAL(18,6),
    order_total DECIMAL(18,6),
    deposit_date DATETIME2,
    expected_delivery DATETIME2,
    status VARCHAR(50),
    notes TEXT,
    sync_status VARCHAR(50) DEFAULT 'pending',
    created_timestamp DATETIME2 DEFAULT CURRENT_TIMESTAMP(),
    synced_timestamp DATETIME2,
    fabric_run_id VARCHAR(255)
);
```

### Balance Staging Table
```sql
CREATE TABLE btmh_balance_staging (
    balance_date DATE,
    store_code VARCHAR(50), 
    account_code VARCHAR(50),
    account_name VARCHAR(255),
    opening_balance DECIMAL(18,6),
    debit_amount DECIMAL(18,6),
    credit_amount DECIMAL(18,6),
    closing_balance DECIMAL(18,6),
    sync_status VARCHAR(50) DEFAULT 'pending',
    created_timestamp DATETIME2 DEFAULT CURRENT_TIMESTAMP(),
    synced_timestamp DATETIME2,
    fabric_run_id VARCHAR(255)
);
```

## 4. Odoo Configuration Steps

### 4.1 Install & Configure BTMH Integration Module

1. Install the `btmh_integration` module
2. Go to **BTMH Integration > Integration > Fabric Pipelines**
3. Create new pipeline records for each data type

### 4.2 Configure Pipeline Records

#### Sales Pipeline Configuration:
```
Name: BTMH Sales Data Pipeline
Fabric Pipeline ID: [YOUR_FABRIC_SALES_PIPELINE_ID]
Fabric Workspace ID: [YOUR_FABRIC_WORKSPACE_ID] 
Pipeline Type: Sales Data
Azure Tenant ID: [YOUR_AZURE_TENANT_ID]
Azure Client ID: [YOUR_AZURE_CLIENT_ID]
Azure Client Secret: [YOUR_AZURE_CLIENT_SECRET]
Pipeline Parameters: {"table_name": "btmh_sales_staging", "batch_size": 1000}
Timeout: 30 minutes
Auto Schedule: True
Schedule Interval: Every 15 Minutes
```

#### Payments Pipeline Configuration:
```
Name: BTMH Payments Data Pipeline  
Fabric Pipeline ID: [YOUR_FABRIC_PAYMENTS_PIPELINE_ID]
Pipeline Type: Payments Data
Schedule Interval: Every 15 Minutes
Pipeline Parameters: {"table_name": "btmh_payments_staging", "batch_size": 500}
```

#### Deposits Pipeline Configuration:
```
Name: BTMH Deposits Data Pipeline
Fabric Pipeline ID: [YOUR_FABRIC_DEPOSITS_PIPELINE_ID] 
Pipeline Type: Deposits Data
Schedule Interval: Every 30 Minutes
Pipeline Parameters: {"table_name": "btmh_deposits_staging", "batch_size": 200}
```

#### Balance Pipeline Configuration:
```
Name: BTMH Daily Balance Pipeline
Fabric Pipeline ID: [YOUR_FABRIC_BALANCE_PIPELINE_ID]
Pipeline Type: Balance Data  
Schedule Interval: Daily
Pipeline Parameters: {"table_name": "btmh_balance_staging", "include_yesterday": true}
```

## 5. Testing the Integration

### 5.1 Test Pipeline Trigger from Odoo
1. Go to **Fabric Pipelines** in Odoo
2. Select a pipeline record  
3. Click **Trigger Pipeline** button
4. Monitor the pipeline execution status

### 5.2 Check Fabric Pipeline Execution
1. Go to Fabric workspace
2. Monitor pipeline runs in Data Factory
3. Check Lakehouse staging tables for new data

### 5.3 Verify Data Sync in Odoo
1. Check **BTMH Integration > Data Management** menus
2. Verify new records are created after pipeline completion
3. Check **Sync Logs** for any errors

## 6. Monitoring & Troubleshooting

### Key Metrics to Monitor:
- Pipeline success/failure rates
- Data sync completeness  
- Average execution times
- Error patterns in logs

### Common Issues:
1. **Authentication Errors**: Check Service Principal permissions
2. **Timeout Issues**: Increase timeout or optimize queries
3. **Data Quality**: Validate source data in BTMH system
4. **Network Issues**: Check connectivity between Fabric and Odoo

### Log Locations:
- Fabric Pipeline Logs: Data Factory monitoring
- Odoo Sync Logs: BTMH Integration > Sync Logs
- System Logs: Odoo server logs

## 7. Production Deployment

### Pre-Production Checklist:
- [ ] Service Principal configured with minimal permissions
- [ ] Pipeline parameters optimized for production load
- [ ] Error handling and retry logic tested
- [ ] Monitoring alerts configured
- [ ] Data backup strategy in place

### Performance Tuning:
- Optimize batch sizes based on data volume
- Configure parallel processing for large datasets  
- Set appropriate timeout values
- Monitor Fabric capacity usage

This solution provides a robust, scalable integration between BTMH POS and Odoo ERP using Microsoft Fabric as the data orchestration layer.
