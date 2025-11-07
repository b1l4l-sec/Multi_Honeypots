# Project Structure

```
multi-honeypot-platform/
│
├── honeypot_modules/              # Python honeypot implementations
│   ├── logger.py                  # Centralized JSON logger (29 lines)
│   ├── ssh_honeypot.py           # SSH honeypot on port 2222 (200 lines)
│   ├── http_honeypot.py          # HTTP honeypot on port 8080 (153 lines)
│   └── ftp_honeypot.py           # FTP honeypot on port 2121 (155 lines)
│
├── elk_config/                    # ELK Stack configuration
│   ├── docker-compose.yml        # ELK 8.15.0 with healthchecks
│   ├── logstash.conf             # Log parsing pipeline (58 lines)
│   ├── kibana_dashboard.ndjson   # Pre-configured dashboard
│   └── GeoLite2-City.mmdb        # GeoIP database (user provided)
│
├── apparmor_profiles/             # Security confinement (optional)
│   ├── ssh_honeypot              # AppArmor profile for SSH
│   ├── http_honeypot             # AppArmor profile for HTTP
│   └── ftp_honeypot              # AppArmor profile for FTP
│
├── requirements.txt               # Python dependencies
│   ├── paramiko==3.3.1           # SSH protocol
│   ├── Flask==3.0.0              # HTTP framework
│   ├── pyftpdlib==1.5.9          # FTP server
│   └── Werkzeug==3.0.1           # WSGI utility
│
├── README.md                      # Project overview
├── DEPLOYMENT.md                  # Complete deployment guide
├── QUICKSTART.md                  # Quick reference
├── CHANGELOG.md                   # Version history
└── PROJECT_STRUCTURE.md           # This file

Log Directory:
/var/log/multi_honeypot/
├── ssh.log                        # SSH events in JSON
├── http.log                       # HTTP events in JSON
└── ftp.log                        # FTP events in JSON
```

## File Descriptions

### Core Honeypots

- **logger.py**: Centralized logging class that writes JSON events to log files
- **ssh_honeypot.py**: SSH server that logs authentication and command attempts
- **http_honeypot.py**: Flask web app with fake admin login panel
- **ftp_honeypot.py**: FTP server with anonymous access enabled

### ELK Configuration

- **docker-compose.yml**: Orchestrates Elasticsearch, Logstash, and Kibana
- **logstash.conf**: Parses JSON logs and enriches with GeoIP data
- **kibana_dashboard.ndjson**: Pre-built visualizations (import in Kibana)
- **GeoLite2-City.mmdb**: MaxMind GeoIP database (download separately)

### Security Profiles

- **apparmor_profiles/**: Optional MAC (Mandatory Access Control) profiles
  - Restrict each honeypot to only its log file
  - Deny access to sensitive directories
  - Limit network capabilities

### Documentation

- **README.md**: Overview, features, quick commands
- **DEPLOYMENT.md**: Step-by-step deployment with all commands
- **QUICKSTART.md**: Condensed reference for experienced users
- **CHANGELOG.md**: Version history and fixes
- **PROJECT_STRUCTURE.md**: This architecture overview

## Data Flow

```
1. Attacker connects → Honeypot (SSH/HTTP/FTP)
2. Honeypot logs event → /var/log/multi_honeypot/*.log (JSON)
3. Logstash reads logs → Parses JSON + adds GeoIP
4. Elasticsearch indexes → Daily indices (honeypot-YYYY.MM.DD)
5. Kibana visualizes → Dashboards, maps, timelines
```

## Key Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| SSH Honeypot | paramiko | 3.3.1 | SSH protocol implementation |
| HTTP Honeypot | Flask | 3.0.0 | Web framework |
| FTP Honeypot | pyftpdlib | 1.5.9 | FTP server library |
| Log Storage | Elasticsearch | 8.15.0 | Search and analytics |
| Log Processing | Logstash | 8.15.0 | Log parser and enricher |
| Visualization | Kibana | 8.15.0 | Dashboard and analytics UI |
| Containerization | Docker | Latest | Service isolation |
| Orchestration | Docker Compose | 3.8 | Multi-container deployment |

## Port Mapping

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| SSH Honeypot | 2222 | TCP | Fake SSH server |
| HTTP Honeypot | 8080 | TCP | Fake web admin |
| FTP Honeypot | 2121 | TCP | Fake FTP server |
| Elasticsearch | 9200 | TCP | REST API |
| Elasticsearch | 9300 | TCP | Node communication |
| Logstash | 5044 | TCP | Beats input (unused) |
| Logstash | 9600 | TCP | Monitoring API |
| Kibana | 5601 | TCP | Web UI |

## Log Format

All logs follow this JSON structure:

```json
{
  "timestamp": "2024-11-06T12:34:56.789Z",
  "ip_address": "192.168.1.100",
  "port": 2222,
  "honeypot_type": "SSH",
  "event_type": "ssh_login_attempt",
  "event_data": {
    "username": "admin",
    "password": "password123",
    "auth_method": "password"
  }
}
```

## System Requirements

- **OS**: Kali Linux or Debian-based
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 20GB free space
- **Docker**: Version 20.10+
- **Python**: Version 3.8+
- **Privileges**: Root/sudo access

## Network Requirements

- All ports (2222, 8080, 2121) must be available
- If using remotely, adjust firewall rules
- For internet-exposed deployment, use caution and isolation

## Development

Total lines of code: ~600 lines
- Python: ~540 lines
- Configuration: ~60 lines
- Documentation: 1000+ lines

Clean, modular architecture following single responsibility principle.
