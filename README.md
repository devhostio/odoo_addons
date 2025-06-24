# Odoo Addons Repository

This repository contains custom Odoo modules for extending functionality in Odoo ERP.

## Modules Overview

| Module | Version | Category | Description | Key Features |
|--------|---------|----------|-------------|--------------|
| **dh_invoice_payment_status** | 18.0.1.0.0 | Sales | Track payment status of sales orders and register payments | • Payment status tracking (No Invoice, Not Paid, Partially Paid, Fully Paid, Overdue)<br>• Register payment button on sale orders<br>• Payment wizard for handling multiple invoices<br>• Automatic status updates based on invoice states<br>• Color-coded status badges |
| **sales_payment_status_app** | 18.0 | Sales | Third-party module for invoice payment status tracking | • Invoice status and payment status display<br>• Payment registration from sale order<br>• Payment details widget<br>• Status filters in tree view<br>• Amount due tracking |

## Installation

1. Clone this repository to your Odoo addons directory
2. Update the addons list in Odoo
3. Install the desired module(s) through the Apps menu

## Module Details

### dh_invoice_payment_status
**Author:** DevHost  
**License:** LGPL-3  
**Dependencies:** sale, account

This module enhances the sales order workflow by adding comprehensive payment tracking capabilities. It automatically computes payment status based on related invoices and provides a streamlined interface for registering payments directly from the sale order form.

### sales_payment_status_app
**Author:** Edge Technologies  
**License:** OPL-1  
**Dependencies:** base, sale_management, stock, account

A third-party module that provides similar payment status tracking functionality with additional features like payment details widgets and enhanced filtering options.

## Contributing

When adding new modules to this repository:
1. Follow Odoo module naming conventions
2. Include a comprehensive `__manifest__.py` file
3. Add proper security access rules
4. Update this README with module information

## Support

For issues or questions regarding these modules, please create an issue in the repository.
