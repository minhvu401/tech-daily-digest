@echo off
:: Tech Daily Digest – Khởi động scheduler 7h sáng mỗi ngày
title Tech Daily Digest Scheduler
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo ========================================
echo  Tech Daily Digest - Scheduler
echo  Email se gui luc 7:00 AM moi ngay
echo  Nhan Ctrl+C de dung
echo ========================================
python main.py
pause
