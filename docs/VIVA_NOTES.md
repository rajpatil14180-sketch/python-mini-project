# Viva Notes: GharPar PG Manager

## What does the project do?
It helps a PG owner see properties, rooms, beds, tenant payment status, maintenance tickets, and announcements. Tenants can view their financial information, announcements, and raise maintenance tickets.

## Why SQLite?
SQLite stores data in a local database file and does not require a separate database server.

## Why Tkinter?
Tkinter is included with Python and provides desktop windows, labels, buttons, forms, and tables.

## Why hash passwords?
The database stores a derived hash and a random salt instead of storing the original password in plain text.

## What is a foreign key?
A foreign key links a record to a related record and helps prevent orphaned data. The application enables SQLite foreign-key enforcement for each connection.

## How is late-join pricing calculated?
The joining date is compared with the college start date. A discount tier is selected, applied using integer arithmetic, and the result is rounded down to the nearest ₹100.

## How are installments calculated?
The yearly agreed price is split into 12 installments. The first 11 use integer division, and the final installment includes any remainder.

## What is an overdue amount?
It is the amount scheduled to be paid by today minus the total amount paid, with a minimum of zero.

## What is intentionally not in the MVP?
Tenant self-booking, reservations, and reservation conflict handling are postponed until after the MVP.
