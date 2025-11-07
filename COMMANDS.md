# Complete Command Reference

All commands needed to run the multi-honeypot platform.

## Quick Start (Copy and Paste)

```bash
# 1. Setup
cd /tmp/cc-agent/59781556/project
sudo mkdir -p /var/log/multi_honeypot
sudo chmod 755 /var/log/multi_honeypot
pip3 install -r requirements.txt

# 2. Start ELK Stack
cd elk_config
docker-compose up -d
sleep 30

# 3. Verify ELK is ready
curl http://localhost:9200/_cluster/health?pretty

# 4. Start Honeypots (open 3 terminals)
# Terminal 1:
cd /tmp/cc-agent/59781556/project/honeypot_modules && python3 ssh_honeypot.py

# Terminal 2:
cd /tmp/cc-agent/59781556/project/honeypot_modules && python3 http_honeypot.py

# Terminal 3:
cd /tmp/cc-agent/59781556/project/honeypot_modules && python3 -m venv venv && source venv/bin/activate && python ftp_honeypot.py # make sure that ftp.log file is created in /var/log/multi_honeypot with the other ssh and http log files
# 5. Test (open 4th terminal)
ssh admin@localhost -p 2222
curl http://localhost:8080
ftp localhost 2121

# 6. View in browser
# http://localhost:5601
```

## Installation Commands

### Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### Install with Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Create Log Directory

```bash
sudo mkdir -p /var/log/multi_honeypot
sudo chmod 755 /var/log/multi_honeypot
```

## Docker Commands

### Start ELK Stack

```bash
cd elk_config
docker-compose up -d
```

### Stop ELK Stack

```bash
cd elk_config
docker-compose down
```

### Restart ELK Stack

```bash
cd elk_config
docker-compose restart
```

### View Container Logs

```bash
docker logs elasticsearch
docker logs logstash -f
docker logs kibana
```

### Check Container Status

```bash
docker ps
docker ps -a
```

### Remove All Data (Fresh Start)

```bash
cd elk_config
docker-compose down -v
docker-compose up -d
```

## Honeypot Commands

### Start SSH Honeypot

```bash
cd honeypot_modules
python3 ssh_honeypot.py
```

### Start HTTP Honeypot

```bash
cd honeypot_modules
python3 http_honeypot.py
```

### Start FTP Honeypot

```bash
cd honeypot_modules
python3 ftp_honeypot.py
```

### Stop Honeypot

Press `Ctrl+C` in the terminal

## Testing Commands

### SSH Tests

```bash
# Manual test
ssh admin@localhost -p 2222

# With password (requires sshpass)
sshpass -p "password123" ssh -o StrictHostKeyChecking=no admin@localhost -p 2222

# Hydra brute force
hydra -l admin -p password123 localhost -s 2222 ssh
hydra -l admin -P /usr/share/wordlists/rockyou.txt localhost -s 2222 ssh

# Multiple attempts
for i in {1..10}; do ssh admin@localhost -p 2222 2>/dev/null; done
```

### HTTP Tests

```bash
# GET request
curl http://localhost:8080

# POST login
curl -X POST http://localhost:8080/login -d "username=admin&password=test123"

# Path probing
curl http://localhost:8080/admin
curl http://localhost:8080/wp-admin
curl http://localhost:8080/phpmyadmin

# Multiple requests
for i in {1..10}; do curl -s http://localhost:8080 > /dev/null; done
```

### FTP Tests

```bash
# Manual test
ftp localhost 2121
# Use username: anonymous, password: <enter>

# Quick test
curl ftp://localhost:2121/

# With authentication
curl -u anonymous: ftp://localhost:2121/
```

### Port Scanning

```bash
# Scan all honeypot ports
nmap -p 2222,8080,2121 -sV localhost

# Aggressive scan
nmap -p 2222,8080,2121 -A localhost
```

## Log Management Commands

### View Logs Real-time

```bash
sudo tail -f /var/log/multi_honeypot/ssh.log
sudo tail -f /var/log/multi_honeypot/http.log
sudo tail -f /var/log/multi_honeypot/ftp.log
```

### View Last 20 Lines

```bash
sudo tail -20 /var/log/multi_honeypot/ssh.log
sudo tail -20 /var/log/multi_honeypot/http.log
sudo tail -20 /var/log/multi_honeypot/ftp.log
```

### View with JSON Formatting

```bash
sudo tail -20 /var/log/multi_honeypot/ssh.log | python3 -m json.tool
```

### Count Log Entries

```bash
wc -l /var/log/multi_honeypot/*.log
```

### Clear Logs

```bash
sudo truncate -s 0 /var/log/multi_honeypot/*.log
```

### Check Log Files Exist

```bash
ls -lh /var/log/multi_honeypot/
```

## Elasticsearch Commands

### Check Health

```bash
curl http://localhost:9200/_cluster/health?pretty
```

### List Indices

```bash
curl http://localhost:9200/_cat/indices?v
```

### Count Documents

```bash
curl http://localhost:9200/honeypot-*/_count?pretty
```

### View Sample Documents

```bash
curl http://localhost:9200/honeypot-*/_search?pretty&size=5
```

### Search for Specific IP

```bash
curl -X GET "localhost:9200/honeypot-*/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "ip_address": "127.0.0.1"
    }
  }
}
'
```

### Delete Indices

```bash
curl -X DELETE "localhost:9200/honeypot-*"
```

## Logstash Commands

### Check Pipeline Status

```bash
curl http://localhost:9600/_node/stats/pipelines?pretty
```

### Check Logstash Health

```bash
curl http://localhost:9600/_node?pretty
```

### Restart Logstash

```bash
docker restart logstash
```

## Kibana Commands

### Access Kibana

```
http://localhost:5601
```

### Create Index Pattern via API

```bash
curl -X POST "localhost:5601/api/saved_objects/index-pattern/honeypot-pattern" \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d'
{
  "attributes": {
    "title": "honeypot-*",
    "timeFieldName": "@timestamp"
  }
}
'
```

## Troubleshooting Commands

### Check Port Usage

```bash
sudo netstat -tulpn | grep -E "2222|8080|2121|9200|5601"
```

### Check Processes

```bash
ps aux | grep python3
ps aux | grep docker
```

### Kill All Honeypots

```bash
sudo pkill -f ssh_honeypot.py
sudo pkill -f http_honeypot.py
sudo pkill -f ftp_honeypot.py
```

### Check Python Dependencies

```bash
pip3 list | grep -E "paramiko|Flask|pyftpdlib"
```

### Test Python Syntax

```bash
cd honeypot_modules
python3 -m py_compile ssh_honeypot.py
python3 -m py_compile http_honeypot.py
python3 -m py_compile ftp_honeypot.py
```

### Check Disk Space

```bash
df -h /var/log/multi_honeypot
```

### Check Memory

```bash
free -h
docker stats
```

## Monitoring Commands

### Watch Logs in Real-time

```bash
watch -n 1 'sudo tail -5 /var/log/multi_honeypot/ssh.log'
```

### Monitor Elasticsearch Documents

```bash
watch -n 2 'curl -s localhost:9200/honeypot-*/_count?pretty'
```

### Monitor Docker Resources

```bash
docker stats
```

## Complete Test Sequence

```bash
#!/bin/bash

echo "=== Testing Multi-Honeypot Platform ==="

echo "1. Testing SSH..."
ssh admin@localhost -p 2222 2>&1 | head -5
sleep 1

echo "2. Testing HTTP..."
curl -s http://localhost:8080 | head -5
sleep 1

echo "3. Testing FTP..."
curl -s ftp://localhost:2121/ 2>&1 | head -5
sleep 1

echo "4. Checking logs..."
sudo ls -lh /var/log/multi_honeypot/
sleep 2

echo "5. Checking Elasticsearch..."
curl -s localhost:9200/honeypot-*/_count?pretty

echo "=== Test Complete ==="
```

## Clean Reinstall Commands

```bash
# Stop everything
pkill -f honeypot.py
cd elk_config && docker-compose down -v

# Clean logs
sudo rm -rf /var/log/multi_honeypot/*

# Restart ELK
docker-compose up -d
sleep 30

# Verify
curl localhost:9200/_cluster/health?pretty
```

## Port Reference

- 2222 - SSH Honeypot
- 8080 - HTTP Honeypot
- 2121 - FTP Honeypot
- 9200 - Elasticsearch
- 9300 - Elasticsearch (cluster communication)
- 5044 - Logstash (Beats input)
- 9600 - Logstash (monitoring API)
- 5601 - Kibana

## File Locations

- Honeypots: `/tmp/cc-agent/59781556/project/honeypot_modules/`
- Logs: `/var/log/multi_honeypot/`
- ELK Config: `/tmp/cc-agent/59781556/project/elk_config/`
- Requirements: `/tmp/cc-agent/59781556/project/requirements.txt`

## Keyboard Shortcuts

- `Ctrl+C` - Stop honeypot
- `Ctrl+Z` - Suspend process
- `Ctrl+D` - Exit SSH/FTP session

## Success Indicators

1. Honeypots show "Listening" message
2. `curl localhost:9200` returns JSON response
3. `ls /var/log/multi_honeypot/` shows 3 log files
4. `curl localhost:9200/_cat/indices?v` shows honeypot-* indices
5. Kibana loads at http://localhost:5601
6. Document count increases after generating traffic
