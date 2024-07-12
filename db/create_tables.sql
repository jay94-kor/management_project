-- db/create_tables.sql

CREATE TABLE Project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    client TEXT NOT NULL,
    pm TEXT NOT NULL,
    department TEXT NOT NULL,
    contract_amount REAL NOT NULL,
    expected_profit REAL NOT NULL,
    expected_profit_rate REAL GENERATED ALWAYS AS (CASE WHEN contract_amount = 0 THEN 0 ELSE expected_profit / contract_amount END) STORED,
    total_expenditure REAL DEFAULT 0,
    balance REAL GENERATED ALWAYS AS (contract_amount - total_expenditure) STORED
);

CREATE TABLE ProjectItem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    item TEXT NOT NULL,
    description TEXT,
    quantity1 INTEGER,
    spec1 TEXT,
    quantity2 INTEGER,
    spec2 TEXT,
    unit_price REAL,
    total_price REAL,
    assigned_amount REAL,
    FOREIGN KEY (project_id) REFERENCES Project(id)
);

CREATE TABLE ExpenditureRequest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    expenditure_type TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (project_id) REFERENCES Project(id)
);