# Entity-Relationship Diagram

## Database Schema Overview

This document describes the database structure for the Remote Monitoring Portal.

---

## Tables and Relationships

### 1. USERS Table
Stores portal users (Admin and regular Users)

| Column Name   | Data Type    | Constraints       | Description                          |
|---------------|--------------|-------------------|--------------------------------------|
| id            | INTEGER      | PRIMARY KEY       | Unique user identifier               |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL  | Login username                       |
| email         | VARCHAR(100) | UNIQUE, NOT NULL  | User email address                   |
| hashed_password| VARCHAR(255)| NOT NULL          | Bcrypt hashed password               |
| role          | VARCHAR(20)  | NOT NULL          | Role: 'admin' or 'user'              |
| is_active     | BOOLEAN      | DEFAULT TRUE      | Account status                       |
| created_at    | DATETIME     | DEFAULT NOW       | Account creation timestamp           |

**Relationships:**
- One user can have many agents assigned (via user_agents)
- One user can send many commands

---

### 2. AGENTS Table
Stores information about Windows agents

| Column Name   | Data Type    | Constraints       | Description                          |
|---------------|--------------|-------------------|--------------------------------------|
| id            | INTEGER      | PRIMARY KEY       | Unique agent identifier              |
| agent_id      | VARCHAR(50)  | UNIQUE, NOT NULL  | Human-readable agent ID              |
| hostname      | VARCHAR(100) | NOT NULL          | Computer name                        |
| ip_address    | VARCHAR(45)  | NULL              | IP address (IPv4 or IPv6)            |
| token         | VARCHAR(255) | UNIQUE, NOT NULL  | Authentication token                 |
| status        | VARCHAR(20)  | DEFAULT 'offline' | Status: 'online' or 'offline'        |
| last_seen     | DATETIME     | NULL              | Last connection timestamp            |
| created_at    | DATETIME     | DEFAULT NOW       | Agent registration timestamp         |

**Relationships:**
- One agent can be assigned to many users (via user_agents)
- One agent has many system_data records
- One agent has many processes
- One agent receives many commands

---

### 3. USER_AGENTS Table (Association Table)
Links users to agents they can access

| Column Name   | Data Type    | Constraints           | Description                     |
|---------------|--------------|-----------------------|---------------------------------|
| id            | INTEGER      | PRIMARY KEY           | Unique record identifier        |
| user_id       | INTEGER      | FOREIGN KEY, NOT NULL | References users.id             |
| agent_id      | INTEGER      | FOREIGN KEY, NOT NULL | References agents.id            |

**Unique Constraint:** (user_id, agent_id) - A user can't be assigned to same agent twice

**Relationships:**
- Many-to-Many relationship between Users and Agents

---

### 4. SYSTEM_DATA Table
Stores system information collected from agents

| Column Name        | Data Type     | Constraints           |  Description                         |
|--------------------|---------------|-----------------------|--------------------------------------|
| id                 | INTEGER       | PRIMARY KEY           | Unique record identifier             |
| agent_id           | INTEGER       | FOREIGN KEY, NOT NULL | References agents.id                 |
| os_name            | VARCHAR(100)  | NULL                  | Operating system name                |
| os_version         | VARCHAR(50)   | NULL                  | OS version                           |
| cpu_model          | VARCHAR(200)  | NULL                  | CPU model name                       |
| cpu_cores          | INTEGER       | NULL                  | Number of CPU cores                  |
| cpu_usage_percent  | FLOAT         | NULL                  | Current CPU usage %                  |
| ram_total_gb       | FLOAT         | NULL                  | Total RAM in GB                      |
| ram_used_gb        | FLOAT         | NULL                  | Used RAM in GB                       |
| ram_usage_percent  | FLOAT         | NULL                  | RAM usage %                          |
| disk_total_gb      | FLOAT         | NULL                  | Total disk space in GB               |
| disk_used_gb       | FLOAT         | NULL                  | Used disk space in GB                |
| disk_usage_percent | FLOAT         | NULL                  | Disk usage %                         |
| uptime_hours       | FLOAT         | NULL                  | System uptime in hours               |
| collected_at       | DATETIME      | DEFAULT NOW           | Data collection timestamp            |

**Relationships:**
- Many system_data records belong to one agent

---

### 5. PROCESSES Table
Stores running processes from agents

| Column Name     | Data Type    | Constraints       | Description                          |
|-----------------|--------------|-------------------|--------------------------------------|
| id              | INTEGER      | PRIMARY KEY       | Unique record identifier             |
| agent_id        | INTEGER      | FOREIGN KEY, NOT NULL | References agents.id             |
| pid             | INTEGER      | NOT NULL          | Process ID                           |
| name            | VARCHAR(200) | NOT NULL          | Process name                         |
| cpu_percent     | FLOAT        | NULL              | CPU usage %                          |
| memory_mb       | FLOAT        | NULL              | Memory usage in MB                   |
| status          | VARCHAR(20)  | NULL              | Process status (running, sleeping)   |
| username        | VARCHAR(100) | NULL              | User running the process             |
| collected_at    | DATETIME     | DEFAULT NOW       | Data collection timestamp            |

**Relationships:**
- Many processes belong to one agent

---

### 6. COMMANDS Table
Stores commands sent from portal to agents

| Column Name   | Data Type     | Constraints           | Description                          |
|---------------|---------------|-----------------------|--------------------------------------|
| id            | INTEGER       | PRIMARY KEY           | Unique command identifier            |
| agent_id      | INTEGER       | FOREIGN KEY, NOT NULL | References agents.id                 |
| user_id       | INTEGER       | FOREIGN KEY, NOT NULL | References users.id (who sent it)    |
| command_type  | VARCHAR(50)   | NOT NULL              | Type: 'refresh_data', 'kill_process' |
| command_data  | TEXT          | NULL                  | Additional command parameters (JSON) |
| status        | VARCHAR(20)   | DEFAULT 'pending'     | Status: pending, executed, failed    |
| result        | TEXT          | NULL                  | Command execution result             |
| created_at    | DATETIME      | DEFAULT NOW           | Command creation timestamp           |
| executed_at   | DATETIME      | NULL                  | Command execution timestamp          |

**Relationships:**
- Many commands belong to one agent
- Many commands are created by one user

---

## Visual ER Diagram

┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    USERS    │────┬────│ USER_AGENTS  │────┬────│   AGENTS    │
│             │    │    │              │    │    │             │
│ PK: id      │    │    │ PK: id       │    │    │ PK: id      │
│    username │    │    │ FK: user_id  │    │    │    agent_id │
│    email    │    │    │ FK: agent_id │    │    │    hostname │
│    password │    │    └──────────────┘    │    │    token    │
│    role     │    │                        │    │    status   │
└─────────────┘    │                        │    └─────────────┘
                   │                        │
                   └────────────────────────┘
                            │
                            │
                  ┌──────────────┐
                  │ SYSTEM_DATA  │
                  │              │
                  │ PK: id       │
                  │ FK: agent_id │───────────────┐
                  │    os_name   │               │
                  │    cpu_usage │               │
                  │    ram_usage │               │
                  └──────────────┘               │
                                                 │
                  ┌──────────────┐               │
                  │  PROCESSES   │               │
                  │              │               │
                  │ PK: id       │               │
                  │ FK: agent_id │───────────────┤
                  │    name      │               │
                  │    pid       │               │
                  │    cpu_usage │               │
                  └──────────────┘               │
                                                 │
                  ┌──────────────┐               │
                  │  COMMANDS    │               │
                  │              │               │
                  │ PK: id       │               │
                  │ FK: agent_id │───────────────┘
                  │ FK: user_id  │
                  │    type      │
                  │    status    │
                  └──────────────┘

---

## Relationships Summary

1. **Users ↔ Agents** (Many-to-Many via USER_AGENTS)
   - An admin can access all agents
   - A regular user can access only assigned agents

2. **Agents ↔ System Data** (One-to-Many)
   - One agent has multiple system data snapshots over time

3. **Agents ↔ Processes** (One-to-Many)
   - One agent has multiple process records

4. **Users ↔ Commands** (One-to-Many)
   - One user can send multiple commands

5. **Agents ↔ Commands** (One-to-Many)
   - One agent receives multiple commands

---

## Indexes for Performance
```sql
-- Speed up user login
CREATE INDEX idx_users_username ON users(username);

-- Speed up agent lookups
CREATE INDEX idx_agents_agent_id ON agents(agent_id);
CREATE INDEX idx_agents_status ON agents(status);

-- Speed up data queries by agent
CREATE INDEX idx_system_data_agent ON system_data(agent_id);
CREATE INDEX idx_processes_agent ON processes(agent_id);
CREATE INDEX idx_commands_agent ON commands(agent_id);

-- Speed up command status queries
CREATE INDEX idx_commands_status ON commands(status);
```

---

## Database Size Estimates (for planning)

Assuming 100 agents, 1000 users:

| Table        | Records/Day | Storage/Day | 30 Days Storage  |
|--------------|-------------|-------------|------------------|
| USERS        | ~10 new     | ~1 KB       | ~30 KB           |
| AGENTS       | ~5 new      | ~500 B      | ~15 KB           |
| SYSTEM_DATA  | ~288,000    | ~50 MB      | ~1.5 GB          |
| PROCESSES    | ~2,880,000  | ~200 MB     | ~6 GB            |
| COMMANDS     | ~10,000     | ~2 MB       | ~60 MB           |

**Total: ~7.5 GB per month**

**Recommendation:** Implement data retention policy (keep last 30 days only)

---

## Security Considerations

1. **Password Storage**: Always use bcrypt hashing, never store plain text
2. **Token Security**: Agent tokens should be long random strings (32+ characters)
3. **SQL Injection**: Using SQLAlchemy ORM prevents SQL injection attacks
4. **Access Control**: Enforce user-agent relationships at application level
5. **Audit Trail**: Commands table provides audit log of who did what

---
