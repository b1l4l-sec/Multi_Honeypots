#!/bin/bash

# Generate test honeypot logs with various IPs for testing

LOG_DIR="/var/log/multi_honeypot"
SSH_LOG="$LOG_DIR/ssh.log"
FTP_LOG="$LOG_DIR/ftp.log"

# Create log directory if it doesn't exist
mkdir -p $LOG_DIR

# Array of public IPs from different countries (these will get real geolocation)
PUBLIC_IPS=(
  "8.8.8.8"           # Google DNS - USA
  "1.1.1.1"           # Cloudflare - USA
  "185.125.190.39"    # Russia
  "103.28.248.2"      # China
  "176.123.26.122"    # Iran
  "80.78.23.45"       # Germany
  "41.60.232.19"      # Nigeria
  "200.110.173.73"    # Brazil
  "122.176.67.90"     # India
  "202.93.128.44"     # Australia
)

# Common usernames tried by attackers
USERNAMES=(
  "root" "admin" "user" "test" "ubuntu" "centos" 
  "oracle" "postgres" "mysql" "ftpuser" "guest"
)

# Generate SSH attack logs
echo "Generating SSH honeypot logs..."
for i in {1..50}; do
  IP=${PUBLIC_IPS[$RANDOM % ${#PUBLIC_IPS[@]}]}
  USERNAME=${USERNAMES[$RANDOM % ${#USERNAMES[@]}]}
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
  
  echo "$TIMESTAMP $IP ssh Login attempt: username=$USERNAME password=password123" >> $SSH_LOG
done

# Generate FTP attack logs (JSON format)
echo "Generating FTP honeypot logs..."
for i in {1..30}; do
  IP=${PUBLIC_IPS[$RANDOM % ${#PUBLIC_IPS[@]}]}
  USERNAME=${USERNAMES[$RANDOM % ${#USERNAMES[@]}]}
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
  
  echo "{\"timestamp\":\"$TIMESTAMP\",\"ip_address\":\"$IP\",\"event_type\":\"ftp_login\",\"username\":\"$USERNAME\",\"password\":\"admin123\"}" >> $FTP_LOG
done

echo "Test logs generated!"
echo "SSH log: $SSH_LOG"
echo "FTP log: $FTP_LOG"
echo ""
echo "Logs will appear in Elasticsearch within 30 seconds"
echo "Check your Kibana dashboard for the geolocation map!"
