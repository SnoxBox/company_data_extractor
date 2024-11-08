-- init.sql
CREATE TABLE IF NOT EXISTS company_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255),
    description TEXT,
    twitter VARCHAR(255),
    status VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    founded INT,
    employee_range VARCHAR(50),
    location VARCHAR(255)
);