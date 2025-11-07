#!/usr/bin/env python3
import socket
import threading
import paramiko
from paramiko.ssh_exception import MessageOrderError, SSHException
from logger import HoneypotLogger
import time
from collections import defaultdict
import logging

logging.getLogger("paramiko").setLevel(logging.CRITICAL)

_last_conn = defaultdict(float)
_MIN_INTERVAL = 0.1


class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip, logger):
        self.client_ip = client_ip
        self.logger = logger
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # Log login attempt but don't let logger failures break auth flow
        try:
            self.logger.log_event(
                ip_address=self.client_ip,
                port=2222,
                event_type="ssh_login_attempt",
                event_data={
                    "username": username,
                    "password": password,
                    "auth_method": "password"
                }
            )
        except Exception:
            pass

        print(f"[SSH] Login attempt from {self.client_ip} - Username: {username}, Password: {password}")
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        try:
            self.logger.log_event(
                ip_address=self.client_ip,
                port=2222,
                event_type="ssh_command_attempt",
                event_data={"command": command.decode('utf-8', errors='ignore')}
            )
        except Exception:
            pass

        print(f"[SSH] Command attempt from {self.client_ip}: {command.decode('utf-8', errors='ignore')}")
        return True


def handle_connection(client, addr, host_key, logger):
    client_ip = addr[0]

    # per-IP rate limiting
    now = time.time()
    if now - _last_conn[client_ip] < _MIN_INTERVAL:
        print(f"[SSH] Throttling rapid connection from {client_ip}")
        try:
            logger.log_event(ip_address=client_ip, port=2222, event_type="ssh_throttle", event_data={"reason": "rate_limit"})
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass
        _last_conn[client_ip] = now
        return
    _last_conn[client_ip] = now

    print(f"[SSH] New connection from {client_ip}")
    try:
        logger.log_event(ip_address=client_ip, port=2222, event_type="ssh_connection", event_data={"status": "connected"})
    except Exception:
        pass

    transport = None
    try:
        client.settimeout(10.0)
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)
        server = SSHServer(client_ip, logger)

        try:
            transport.start_server(server=server)
        except (MessageOrderError, SSHException, EOFError) as e:
            return
        except Exception as e:
            return

        try:
            channel = transport.accept(20)
        except (MessageOrderError, SSHException, EOFError):
            return
        except Exception:
            return

        if channel is None:
            print(f"[SSH] No channel from {client_ip}")
            return

        server.event.wait(10)

        if channel.recv_ready():
            command = channel.recv(1024)
            try:
                logger.log_event(ip_address=client_ip, port=2222, event_type="ssh_command_received",
                                event_data={"command": command.decode('utf-8', errors='ignore')})
            except Exception:
                pass

        try:
            channel.send(b"Access denied\r\n")
        except Exception:
            pass
        try:
            channel.close()
        except Exception:
            pass

    finally:
        # cleanup - close transport & socket but don't raise
        try:
            if transport is not None:
                transport.close()
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass


def main():
    HOST = '0.0.0.0'
    PORT = 2222
    logger = HoneypotLogger(honeypot_type="SSH")
    host_key = paramiko.RSAKey.generate(2048)
    print(f"[SSH] Starting SSH honeypot on {HOST}:{PORT}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
    except Exception as e:
        print(f"[SSH] Failed to bind to {HOST}:{PORT}: {e}")
        return
        
    server_socket.listen(100)

    print(f"[SSH] Listening for connections...")

    try:
        while True:
            try:
                client, addr = server_socket.accept()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                # transient accept error: sleep briefly and continue
                print(f"[SSH] Error accepting connection: {e}")
                time.sleep(0.1)
                continue

            # spawn handler thread
            thread = threading.Thread(target=handle_connection, args=(client, addr, host_key, logger))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\n[SSH] Shutting down...")
    finally:
        try:
            server_socket.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
