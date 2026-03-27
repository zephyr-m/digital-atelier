#!/bin/bash
set -a
source /home/zephyr/dev/spirit-shop/.env
set +a
exec python3 /home/zephyr/dev/spirit-shop/bot.py
