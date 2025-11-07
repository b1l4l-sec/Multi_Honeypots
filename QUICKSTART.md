# Quick Start Guide

## 1. Prerequisites Check

```bash
# Verify Docker is installed and running
docker --version
docker-compose --version
sudo systemctl status docker

# Check available memory (need 4GB+)
free -h

# Check disk space (need 20GB+)
df -h
```

## 2. Setup (5 minutes)

```bash
# Create log directory
sudo mkdir -p /var/log/multi_honeypot
sudo chmod 755 /var/log/multi_honeypot

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Start ELK Stack (2-3 minutes)

```bash
# Start containers
cd elk_config
docker-compose up -d

# Wait for Elasticsearch to be ready (check until status is yellow/green)
watch -n 2 'curl -s http://localhost:9200/_cluster/health | jq .'

# Verify all services are healthy
docker ps
```

## 4. Start Honeypots (3 terminals)

### Terminal 1
```bash
cd honeypot_modules
source ../venv/bin/activate
sudo -E python3 ssh_honeypot.py
```

### Terminal 2
```bash
cd honeypot_modules
source ../venv/bin/activate
sudo -E python3 http_honeypot.py
```

### Terminal 3
```bash
cd honeypot_modules
source ../venv/bin/activate
sudo -E python3 ftp_honeypot.py
```

## 5. Generate Test Traffic

```bash
# SSH attacks
ssh admin@localhost -p 2222
hydra -l admin -p password localhost -s 2222 ssh

# HTTP attacks
curl -X POST http://localhost:8080/login -d "username=admin&password=test"

# FTP attacks
ftp localhost 2121

# Port scan
nmap -p 2222,8080,2121 -sV localhost
```

## 6. View Results

### Check Logs
```bash
sudo tail -f /var/log/multi_honeypot/*.log | jq .
```

### Check Elasticsearch Indices
```bash
curl http://localhost:9200/_cat/indices?v
curl http://localhost:9200/honeypot-*/_count?pretty
```

### Access Kibana
```
http://localhost:5601
```

1. Go to Management → Data Views
2. Create data view with pattern: `honeypot-*`
3. Set time field: `@timestamp`
4. Go to Discover to see events

## 7. Verify Everything Works

```bash
# All 3 honeypots should be listening
sudo netstat -tulpn | grep -E "2222|8080|2121"

# Log files should have data
ls -lh /var/log/multi_honeypot/

# Elasticsearch should have indices
curl http://localhost:9200/_cat/indices?v | grep honeypot

# Kibana should be accessible
curl -I http://localhost:5601
```

## Common Issues

### No indices in Elasticsearch?
```bash
# Check log files exist
ls -lh /var/log/multi_honeypot/

# Restart Logstash
docker restart logstash

# Check Logstash logs
docker logs logstash --tail 50
```

### Honeypot won't start?
```bash
# Kill existing process
sudo fuser -k 2222/tcp

# Check Python packages
pip list | grep -E "paramiko|Flask|pyftpdlib"
```

### Kibana shows no data?
```bash
# Check time range (set to "Last 15 minutes")
# Refresh the data view fields
# Verify index pattern is honeypot-*
```

## Stop Everything

```bash
# Stop honeypots: Ctrl+C in each terminal

# Stop ELK
cd elk_config
docker-compose down
```

## Complete Deployment Guide

For detailed instructions, see **[DEPLOYMENT.md](DEPLOYMENT.md)**

## Important

template te send data to E 
command : curl -X PUT "localhost:9200/_index_template/honeypot-template" \
 -H "Content-Type: application/json" \
 -d "
{"index_templates":[{"name":"honeypot-template","index_template":{"index_patterns":["honeypot-*"],"template":{"settings":{"index":{"number_of_shards":"1","number_of_replicas":"0","refresh_interval":"5s"}},"mappings":{"properties":{"password":{"type":"text","fields":{"keyword":{"type":"keyword"}}},"@timestamp":{"type":"date"},"geoip":{"properties":{"geo":{"properties":{"city_name":{"type":"keyword"},"country_iso_code":{"type":"keyword"},"timezone":{"type":"keyword"},"country_name":{"type":"keyword"},"continent_code":{"type":"keyword"},"location":{"type":"geo_point"},"region_name":{"type":"keyword"}}},"ip":{"type":"ip"}}},"event_type":{"type":"keyword"},"ip_address":{"type":"ip"},"event_data":{"type":"text"},"timestamp":{"type":"date"},"username":{"type":"text","fields":{"keyword":{"type":"keyword"}}},"tags":{"type":"keyword"}}}},"composed_of":[],"priority":500}}]}  "

