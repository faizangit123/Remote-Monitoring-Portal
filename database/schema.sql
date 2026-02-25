-- Remote Monitoring Portal Database Schema
-- SQLite Database

-- ==============================================
-- TABLE: users
-- Stores portal users (Admin and User roles)
-- ==============================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'user')),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: agents
-- Stores Windows agents being monitored
-- ==============================================
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR(50) UNIQUE NOT NULL,
    hostname VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'offline' CHECK(status IN ('online', 'offline')),
    last_seen DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLE: user_agents
-- Association table: Which users can access which agents
-- ==============================================
CREATE TABLE user_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    UNIQUE(user_id, agent_id)
);

-- ==============================================
-- TABLE: system_data
-- Stores system information from agents
-- ==============================================
CREATE TABLE system_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    os_name VARCHAR(100),
    os_version VARCHAR(50),
    cpu_model VARCHAR(200),
    cpu_cores INTEGER,
    cpu_usage_percent REAL,
    ram_total_gb REAL,
    ram_used_gb REAL,
    ram_usage_percent REAL,
    disk_total_gb REAL,
    disk_used_gb REAL,
    disk_usage_percent REAL,
    uptime_hours REAL,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- ==============================================
-- TABLE: processes
-- Stores running processes from agents
-- ==============================================
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    pid INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    cpu_percent REAL,
    memory_mb REAL,
    status VARCHAR(20),
    username VARCHAR(100),
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- ==============================================
-- TABLE: commands
-- Stores commands sent to agents
-- ==============================================
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    command_type VARCHAR(50) NOT NULL,
    command_data TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK(status IN ('pending', 'executing', 'executed', 'failed')),
    result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    executed_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==============================================
-- INDEXES for Performance
-- ==============================================

-- User lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Agent lookups
CREATE INDEX idx_agents_agent_id ON agents(agent_id);
CREATE INDEX idx_agents_status ON agents(status);

-- User-Agent associations
CREATE INDEX idx_user_agents_user ON user_agents(user_id);
CREATE INDEX idx_user_agents_agent ON user_agents(agent_id);

-- System data queries
CREATE INDEX idx_system_data_agent ON system_data(agent_id);
CREATE INDEX idx_system_data_collected ON system_data(collected_at);

-- Process queries
CREATE INDEX idx_processes_agent ON processes(agent_id);
CREATE INDEX idx_processes_collected ON processes(collected_at);

-- Command queries
CREATE INDEX idx_commands_agent ON commands(agent_id);
CREATE INDEX idx_commands_user ON commands(user_id);
CREATE INDEX idx_commands_status ON commands(status);
CREATE INDEX idx_commands_created ON commands(created_at);

-- ==============================================
-- SAMPLE DATA INSERTION
-- ==============================================

-- Insert admin user (password: admin123)
INSERT INTO users (username, email, hashed_password, role) VALUES 
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NN.1BF1qwhau', 'admin');

-- Insert regular user (password: user123)
INSERT INTO users (username, email, hashed_password, role) VALUES 
('testuser_1', 'testuser@example.com', '$2b$12$WQs2kXZ5qYqWz7UBfxCQFOG3c3e3qF7qJYhRqxDQBKbHfR7xNxBmO', 'user');

-- Insert sample agent
INSERT INTO agents (agent_id, hostname, ip_address, token, status) VALUES 
('agent-001', 'DESKTOP-ABC123', '192.168.1.100', 'my-secret-agent-token-12345', 'offline');

-- Assign all agents to admin (admins can see all agents)
-- Assign specific agent to testuser_1
INSERT INTO user_agents (user_id, agent_id) VALUES 
(1, 1),  -- admin can access agent-001
(2, 1);  -- testuser_1 can access agent-001