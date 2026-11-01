# NEXUS AI — Troubleshooting & Common Issues Guide

### 1. PowerShell Script Execution Policy Error
**Symptom:**  
`File Activate.ps1 cannot be loaded because running scripts is disabled on this system.`  
**Solution:**  
Open PowerShell and run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. npm Execution Policy on Windows
**Symptom:**  
`npm.ps1 cannot be loaded because running scripts is disabled.`  
**Solution:**  
Explicitly run `npm.cmd` instead of `npm`, or execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

### 3. Port 8000 or 5173 Already in Use
**Symptom:**  
`[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`  
**Solution:**  
Find and terminate the occupying process in PowerShell:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### 4. Telegram Bot Updates Not Received
**Symptom:**  
The bot starts but does not reply to Telegram messages.  
**Solution:**
1. Check that `TELEGRAM_BOT_TOKEN` in `.env` is exact.
2. If the bot was previously configured with a webhook, remove the webhook so long polling can receive updates:
   ```powershell
   python -c "import httpx; httpx.get('https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook')"
   ```

### 5. Gemini API Rate Limits or Network Glitches
**Symptom:**  
Gemini requests time out or return 503 / 429 quota errors.  
**Solution:**  
Set `AI_MOCK_MODE=true` in `.env`. NEXUS AI will instantly switch to its internal rule-based intent engine with 0 downtime and 0 token cost.
