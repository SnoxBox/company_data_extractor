-- init.sql
-- Create the database
CREATE DATABASE IF NOT EXISTS companies;

-- Create the user
CREATE USER IF NOT EXISTS 'app'@'%' IDENTIFIED BY 'password123';

-- Grant privileges to the user on the companies database
GRANT ALL PRIVILEGES ON companies.* TO 'app'@'%';

-- Apply the changes (flush privileges)
FLUSH PRIVILEGES;

-- Switch to the companies database
USE companies;

-- Create the company_info table
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
