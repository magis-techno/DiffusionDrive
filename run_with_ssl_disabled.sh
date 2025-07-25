#!/bin/bash

# 禁用SSL验证
export PYTHONHTTPSVERIFY=0
export CURL_CA_BUNDLE=""
export REQUESTS_CA_BUNDLE=""
export PYTHONWARNINGS="ignore:Unverified HTTPS request"

# 禁用urllib3的SSL警告
export PYTHONDONTWRITEBYTECODE=1

# 在Python中禁用SSL验证
export PYTHONSTARTUP="
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
"

echo "SSL verification disabled. Running command: $@"

# 执行传入的命令
exec "$@" 