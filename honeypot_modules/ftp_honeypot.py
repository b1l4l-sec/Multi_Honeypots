#!/usr/bin/env python3
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from logger import HoneypotLogger
import os


class HoneypotFTPHandler(FTPHandler):
    """
    Custom FTP handler that logs honeypot events via HoneypotLogger.
    The logger will be available as self.logger for each handler instance.
    """

    # class-level default logger (will be set by main)
    logger = None

    def __init__(self, *args, **kwargs):
        # allow passing a logger during instantiation, otherwise fall back to class logger
        instance_logger = kwargs.pop("logger", None)
        if instance_logger is not None:
            self.logger = instance_logger
        super().__init__(*args, **kwargs)

    def on_connect(self):
        client_ip = self.remote_ip
        print(f"[FTP] New connection from {client_ip}")

        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_connection",
                event_data={"status": "connected"}
            )

    def on_disconnect(self):
        client_ip = self.remote_ip
        print(f"[FTP] Disconnected from {client_ip}")

        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_disconnection",
                event_data={"status": "disconnected"}
            )

    def on_login(self, username):
        client_ip = self.remote_ip
        print(f"[FTP] Login from {client_ip} - Username: {username}")

        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_login",
                event_data={
                    "username": username,
                    "status": "success"
                }
            )

    def on_login_failed(self, username, password):
        client_ip = self.remote_ip
        print(f"[FTP] Failed login from {client_ip} - Username: {username}, Password: {password}")

        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_login_failed",
                event_data={
                    "username": username,
                    "password": password
                }
            )

    def on_file_sent(self, file):
        client_ip = self.remote_ip
        print(f"[FTP] File downloaded by {client_ip}: {file}")

        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_download",
                event_data={
                    "filename": file,
                    "username": getattr(self, "username", None)
                }
            )

    def on_file_received(self, file):
        client_ip = self.remote_ip
        print(f"[FTP] File uploaded by {client_ip}: {file}")

        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_upload",
                event_data={
                    "filename": file,
                    "username": getattr(self, "username", None)
                }
            )

    def on_incomplete_file_sent(self, file):
        client_ip = self.remote_ip
        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_incomplete_download",
                event_data={
                    "filename": file,
                    "username": getattr(self, "username", None)
                }
            )

    def on_incomplete_file_received(self, file):
        client_ip = self.remote_ip
        if self.logger:
            self.logger.log_event(
                ip_address=client_ip,
                port=2121,
                event_type="ftp_incomplete_upload",
                event_data={
                    "filename": file,
                    "username": getattr(self, "username", None)
                }
            )


def main():
    HOST = "0.0.0.0"
    PORT = 2121

    # create logger instance
    logger = HoneypotLogger(honeypot_type="FTP")

    # ensure ftp directory exists and has proper perms
    ftp_dir = "/tmp/ftp_honeypot"
    os.makedirs(ftp_dir, exist_ok=True)

    # authorizer: anonymous with read/write permissions
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(ftp_dir, perm="elradfmw")

    # configure handler class attributes
    HoneypotFTPHandler.authorizer = authorizer
    HoneypotFTPHandler.banner = "FTP Server Ready"
    HoneypotFTPHandler.logger = logger  # class-level default logger

    # create and run server with the handler class (not a function)
    server = FTPServer((HOST, PORT), HoneypotFTPHandler)

    print(f"[FTP] Starting FTP honeypot on {HOST}:{PORT}")
    print(f"[FTP] Anonymous access enabled with write permissions")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[FTP] Shutting down...")
    finally:
        server.close_all()


if __name__ == "__main__":
    main()
