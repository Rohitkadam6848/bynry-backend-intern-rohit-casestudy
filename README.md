# Bynry Backend Intern - Case Study Solution
**Name:** Your Full Name  
**Email:** your@email.com  
**Date:** April 2026

---

## Part 1: Code Review & Debugging

### Issues Found
1. **No transaction atomicity** - Two separate commits can cause...
2. **No input validation** - Missing fields cause KeyError...
3. **No SKU uniqueness check** - Duplicate SKUs possible...
(list all issues)

### Fixed Code
(paste corrected code here with comments)

---

## Part 2: Database Design

### Schema
(paste SQL DDL here)

### Design Decisions
- Used NUMERIC(12,2) for price because...
- Added inventory_transactions table because...

### Questions for Product Team
1. Is SKU scoped per company or global?
2. How is bundle stock calculated?
(list all your questions)

---

## Part 3: API Implementation

### Assumptions Made
- "Recent sales" = last 30 days
- Low stock threshold stored on products table
- Only preferred supplier returned

### Implementation
(paste your API code here)

### Edge Cases Handled
- Company not found → 404
- No supplier linked → returns null
- Zero daily sales → days_until_stockout returns null

---

## Overall Assumptions & Trade-offs
(Brief summary paragraph)
