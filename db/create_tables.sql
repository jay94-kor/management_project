-- db/create_tables.sql

CREATE TABLE Project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code TEXT NOT NULL UNIQUE,
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
    project_code TEXT NOT NULL,
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
    FOREIGN KEY (project_id) REFERENCES Project(id),
    FOREIGN KEY (project_code) REFERENCES Project(project_code)
);

CREATE TABLE ExpenditureRequest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    project_code TEXT NOT NULL,
    amount REAL NOT NULL,
    expenditure_type TEXT NOT NULL,
    reason TEXT,
    planned_date DATE,
    file_name TEXT,
    file_contents BLOB,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Project(id),
    FOREIGN KEY (project_code) REFERENCES Project(project_code)
);

CREATE TABLE BudgetTransferLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_item_id INTEGER NOT NULL,
    to_item_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    transfer_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_item_id) REFERENCES ProjectItem(id),
    FOREIGN KEY (to_item_id) REFERENCES ProjectItem(id)
);