-- =====================================================
-- Retail Analytics Data Warehouse - Star Schema DDL
-- Database: retail_db
-- =====================================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS retail_db;
USE retail_db;

-- =====================================================
-- DIMENSION TABLES
-- =====================================================

-- -----------------------------------------------------
-- dim_product: Product master data
-- Source: Product ID, Category, Sub-Category, Product Name
-- -----------------------------------------------------
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL,
    product_name VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_sub_category (sub_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- dim_customer: Customer master data
-- Source: Customer ID, Customer Name, Segment
-- -----------------------------------------------------
DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer (
    customer_key INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(200) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_segment (segment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- dim_location: Geographic hierarchy
-- Source: Country, State, City, Postal Code, Region
-- -----------------------------------------------------
DROP TABLE IF EXISTS dim_location;
CREATE TABLE dim_location (
    location_key INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_country (country),
    INDEX idx_state (state),
    INDEX idx_region (region),
    INDEX idx_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- dim_date: Time dimension for date intelligence
-- Source: Derived from Order Date
-- -----------------------------------------------------
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_month INT NOT NULL,
    month INT NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_year (year),
    INDEX idx_month (month),
    INDEX idx_quarter (quarter)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------
-- dim_store: Synthetic store assignments
-- Source: Generated (Store_1 to Store_5)
-- -----------------------------------------------------
DROP TABLE IF EXISTS dim_store;
CREATE TABLE dim_store (
    store_key INT AUTO_INCREMENT PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL UNIQUE,
    store_name VARCHAR(100) NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- FACT TABLE
-- =====================================================

-- -----------------------------------------------------
-- sales_fact: Transactional sales data
-- Contains measures: Sales, Quantity, Discount, Profit
-- Foreign keys to all dimension tables
-- -----------------------------------------------------
DROP TABLE IF EXISTS sales_fact;
CREATE TABLE sales_fact (
    sales_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_date TIMESTAMP NULL,
    ship_date TIMESTAMP NULL,
    ship_mode VARCHAR(50) NOT NULL,
    
    -- Foreign Keys
    product_key INT NOT NULL,
    customer_key INT NOT NULL,
    location_key INT NOT NULL,
    date_key INT NOT NULL,
    store_key INT NOT NULL,

    -- Measures
    sales DECIMAL(15, 2) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 4) NOT NULL,
    profit DECIMAL(15, 2) NOT NULL,
    revenue DECIMAL(15, 2) NOT NULL,

    -- Derived fields
    order_year INT NOT NULL,
    order_month INT NOT NULL,
    order_day INT NOT NULL,
    day_of_week INT NOT NULL,
    is_weekend BOOLEAN NOT NULL,

    -- Audit columns
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    CONSTRAINT fk_product FOREIGN KEY (product_key) 
        REFERENCES dim_product(product_key),
    CONSTRAINT fk_customer FOREIGN KEY (customer_key) 
        REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_location FOREIGN KEY (location_key) 
        REFERENCES dim_location(location_key),
    CONSTRAINT fk_date FOREIGN KEY (date_key) 
        REFERENCES dim_date(date_key),
    CONSTRAINT fk_store FOREIGN KEY (store_key) 
        REFERENCES dim_store(store_key),
    
    -- Indexes for query performance
    INDEX idx_order_id (order_id),
    INDEX idx_order_date (order_date),
    INDEX idx_product_key (product_key),
    INDEX idx_customer_key (customer_key),
    INDEX idx_date_key (date_key),
    INDEX idx_store_key (store_key),
    INDEX idx_year_month (order_year, order_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- END OF SCHEMA
-- =====================================================
