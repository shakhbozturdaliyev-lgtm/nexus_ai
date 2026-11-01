# NEXUS AI — Windows 11 Local Setup & Execution Guide

Welcome to **NEXUS AI**, the intelligent multilingual Telegram customer support platform!
This guide is written for engineers and beginners running Windows 11.

---

## 1. Prerequisites Checklist

Before beginning, ensure you have the following installed on Windows 11:
1. **Python 3.12 or later** ([python.org](https://www.python.org/downloads/))  
   *Note: During installation, check the box "Add python.exe to PATH".*
2. **Node.js 18 or later** ([nodejs.org](https://nodejs.org/))
3. **Git for Windows** ([git-scm.com](https://git-scm.com/))
4. **PowerShell** (built into Windows 11)

---

## 2. Setting Up the Project in PowerShell

Open a PowerShell terminal and navigate to the project directory:

```powershell
cd "d:\antigravity projects\ai agent"
```

### 2.1 Allow PowerShell Script Execution (If Required)
If PowerShell prevents activating virtual environments, run this in your terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2.2 Create & Activate Python Virtual Environment
```powershell
# Create virtual environment inside backend/.venv
python -m venv backend\.venv

# Activate the virtual environment
.\backend\.venv\Scripts\Activate.ps1
```
*(Your prompt will now show `(.venv)` at the beginning).*

### 2.3 Install Backend Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

### 2.4 Configure Environment Variables
Copy the example configuration to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` in your text editor (VS Code, Notepad, etc.) to configure your keys.

---

## 3. Configuring Telegram Bot & Google Gemini

### 3.1 Telegram Bot (Optional for tests; Required for live Telegram chat)
1. Open Telegram and search for `@BotFather`.
2. Send `/newbot`.
3. Choose a name (e.g. `Demo Electronics Support`) and a username ending in `bot` (e.g. `DemoElectronicsSupportBot`).
4. Copy the API Token provided by BotFather (looks like `123456789:ABCdefGHI...`).
5. Paste it into your `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...
   ```

### 3.2 Google Gemini API (Optional)
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Click **Get API key** and generate a new key.
3. Paste it into `.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...
   GEMINI_MODEL=gemini-2.5-flash
   ```
> 💡 **Zero-Cost Development Note**: If `GEMINI_API_KEY` is left blank or `AI_MOCK_MODE=true` is set, NEXUS AI automatically activates its **Built-In Mock AI Engine**. It performs identical product searches, stock checks, and policy matching offline with 0 API cost!

---

## 4. Install Frontend Dependencies

Open a second PowerShell terminal:
```powershell
cd "d:\antigravity projects\ai agent\frontend"
npm.cmd install
```

---

## 5. Running the Application Services

You can run the platform in 3 separate PowerShell terminal windows:

### Terminal 1: FastAPI Backend (Port 8000)
```powershell
cd "d:\antigravity projects\ai agent"
.\backend\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```
- Open your browser to verify:
  - **Health check**: `http://localhost:8000/api/health`
  - **Interactive API Docs (Swagger)**: `http://localhost:8000/docs`

### Terminal 2: Telegram Bot Worker (Long Polling)
```powershell
cd "d:\antigravity projects\ai agent"
.\backend\.venv\Scripts\Activate.ps1
python scripts\run_bot.py
```
- Open Telegram, search for your bot, and send `/start`.

### Terminal 3: React Admin Dashboard (Port 5173)
```powershell
cd "d:\antigravity projects\ai agent\frontend"
npm.cmd run dev
```
- Open `http://localhost:5173` in your browser.
- **Default Login Credentials:**
  - **Owner / Admin**: `admin@demoelectronics.uz` / `AdminPass123!`
  - **Support Operator**: `operator@demoelectronics.uz` / `OperatorPass123!`

---

## 6. Running Automated Tests

Run the full automated test suite (47 tests across unit, integration, security, and E2E scenarios):
```powershell
cd "d:\antigravity projects\ai agent"
.\backend\.venv\Scripts\pytest.exe -c backend\pytest.ini backend\tests
```

---

## 7. Stopping Services Safely

To shut down any running service, press `Ctrl + C` in its respective terminal window.
To deactivate the virtual environment:
```powershell
deactivate
```
