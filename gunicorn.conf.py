import os
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = 2
timeout = 30
accesslog = "-"
errorlog = "-"
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")
limit_request_line = 4094
limit_request_field_size = 8190
preload_app = True  # tạo SECRET_KEY/DB một lần trước khi fork worker
