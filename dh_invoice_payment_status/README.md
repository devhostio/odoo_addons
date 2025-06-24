# Sale Order Payment Status Module for Odoo 18.0

This module adds comprehensive payment status tracking to Odoo sales orders, allowing you to monitor invoice payment states directly from the sale order interface.

## Features

### 1. Payment Status Field
Adds a computed payment status field to sales orders with the following states:
- **No Invoice**: When no invoice has been created for the sale order
- **Not Paid**: When invoices exist but none are paid
- **Partially Paid**: When some invoices are partially paid or some are fully paid while others are not
- **Fully Paid**: When all invoices related to the sale order are fully paid
- **Overdue**: When any invoice has passed its due date without being fully paid

### 2. Register Payment Button
- Adds a "Register Payment" button directly on the sale order form
- Opens a wizard to quickly register payments for unpaid invoices
- Automatically reconciles payments with the selected invoices
- Only visible when there are unpaid invoices

### 3. Enhanced Views
- **Tree View**: Shows payment status with color-coded badges
- **Form View**: Displays payment status in the header with the Register Payment button
- **Kanban View**: Shows payment status on kanban cards
- **Search View**: Adds filters to search by payment status and group by payment status

### 4. Automatic Status Updates
- Payment status automatically updates when:
  - Invoices are created from the sale order
  - Payments are registered on invoices
  - Invoice due dates pass (for overdue status)

## Installation

1. Copy the module to your Odoo addons directory
2. Update the module list in Odoo
3. Install the "Sale Order Payment Status" module

## Usage

1. **View Payment Status**: 
   - Open any sale order to see its current payment status
   - Use the list view to see payment status for multiple orders at once

2. **Register Payments**:
   - Click the "Register Payment" button on a sale order
   - Select the payment amount, date, and journal
   - Click "Create Payment" to register and reconcile the payment

3. **Filter Orders**:
   - Use the search filters to find orders by payment status
   - Group orders by payment status for better overview

## Technical Details

- **Dependencies**: sale, account
- **Models Extended**: sale.order
- **New Models**: sale.payment.wizard
- **License**: LGPL-3

## Security

- All users can view payment status
- Only users with accounting invoice permissions can register payments

## Compatibility

This module is designed for Odoo 18.0 and leverages the latest Odoo features for optimal performance and user experience.
