@echo off
:: Gửi email test ngay lập tức
title Tech Daily Digest - TEST
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo Dang gui email thu...
python main.py --test
pause
