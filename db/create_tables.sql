-- db/create_tables.sql

CREATE TABLE Project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    client TEXT NOT NULL,
    pm TEXT NOT NULL,
    department TEXT NOT NULL,
    contract_amount REAL NOT NULL,
    expected_profit REAL NOT NULL,
    expected_profit_rate REAL GENERATED ALWAYS AS (expected_profit / contract_amount) STORED,
    total_expenditure REAL DEFAULT 0,
    balance REAL GENERATED ALWAYS AS (contract_amount - total_expenditure) STORED
);

CREATE TABLE ProjectItem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    item TEXT NOT NULL,
    description TEXT,
    quantity INTEGER,
    unit TEXT,
    period INTEGER,
    period_unit TEXT,
    unit_price REAL,
    total_price REAL,
    assigned_amount REAL,
    FOREIGN KEY (project_id) REFERENCES Project(id)
);

CREATE TABLE ExpenditureRequest (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_item_id INTEGER NOT NULL,
    requested_amount REAL NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (project_item_id) REFERENCES ProjectItem(id)
);