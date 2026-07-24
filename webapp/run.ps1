# 画像解析デモ Web版 起動スクリプト
# 使い方: プロジェクトルート(imageanalyze)で  .\webapp\run.ps1
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& "$root\Scripts\python.exe" -m uvicorn webapp.main:app --host 127.0.0.1 --port 8000 --reload
