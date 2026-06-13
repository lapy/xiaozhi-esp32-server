-- H2 Database schema for testing
-- This script creates the necessary tables for testing

-- Create sys_user table
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100),
    salt VARCHAR(20),
    mobile VARCHAR(20),
    super_admin TINYINT DEFAULT 0,
    status TINYINT DEFAULT 1,
    updater BIGINT,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creator BIGINT,
    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sys_role table
CREATE TABLE IF NOT EXISTS sys_role (
    id BIGINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    remark VARCHAR(100),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sys_user_role table
CREATE TABLE IF NOT EXISTS sys_user_role (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES sys_user(id),
    FOREIGN KEY (role_id) REFERENCES sys_role(id)
);

-- Create sys_menu table
CREATE TABLE IF NOT EXISTS sys_menu (
    id BIGINT PRIMARY KEY,
    parent_id BIGINT,
    name VARCHAR(50) NOT NULL,
    url VARCHAR(200),
    perms VARCHAR(500),
    type TINYINT,
    icon VARCHAR(50),
    order_num INT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sys_role_menu table
CREATE TABLE IF NOT EXISTS sys_role_menu (
    id BIGINT PRIMARY KEY,
    role_id BIGINT NOT NULL,
    menu_id BIGINT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES sys_role(id),
    FOREIGN KEY (menu_id) REFERENCES sys_menu(id)
);

-- Create device_info table
CREATE TABLE IF NOT EXISTS device_info (
    id BIGINT PRIMARY KEY,
    mac_address VARCHAR(50) NOT NULL,
    device_code VARCHAR(50),
    board VARCHAR(100),
    app_version VARCHAR(50),
    status TINYINT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sys_params table
CREATE TABLE IF NOT EXISTS sys_params (
    id BIGINT PRIMARY KEY,
    param_code VARCHAR(50) NOT NULL,
    param_value VARCHAR(500),
    remark VARCHAR(200),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test data
INSERT INTO sys_user (id, username, password, salt, mobile, status) VALUES 
(1, 'admin', 'admin123', 'salt123', '13800138000', 1),
(2, 'test', 'test123', 'salt456', '13800138001', 1);

INSERT INTO sys_role (id, name, remark) VALUES 
(1, 'admin', 'Administrator'),
(2, 'user', 'Regular User');

INSERT INTO sys_user_role (id, user_id, role_id) VALUES 
(1, 1, 1),
(2, 2, 2);

-- Insert test system parameters
INSERT INTO sys_params (id, param_code, param_value, remark) VALUES 
(1, 'server.allow_user_register', 'true', 'Allow user registration'),
(2, 'server.enable_mobile_register', 'false', 'Enable mobile registration'),
(3, 'DEFAULT_PASSWORD', '123456', 'Default password for new users'),
(4, 'SESSION_TIMEOUT', '1800', 'Session timeout in seconds');