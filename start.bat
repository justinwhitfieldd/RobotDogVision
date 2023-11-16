@echo off
start cmd.exe /k "node go1-service.js"
start cmd.exe /k "flask run --port=5001 --host=0.0.0.0 --cert=adhoc"
