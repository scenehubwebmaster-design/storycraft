# Network Access Troubleshooting Guide

## Issue: Characters not loading when accessing from mobile device

### Symptoms

- App loads on mobile but Characters page shows loading spinner or error
- Works fine on localhost but not on network IP (192.168.x.x)
- Backend appears to be running

### Diagnostic Steps

#### 1. Verify Backend is Running and Accessible

**Check if backend is running:**

```powershell
# Should show backend running on 0.0.0.0:8000
Get-Process -Name python | Where-Object {$_.MainWindowTitle -like "*uvicorn*"}
```

**Test backend locally:**

```powershell
# Should return: {"status": "healthy"}
curl http://localhost:8000/health

# Should return characters array
curl http://localhost:8000/api/characters
```

**Test backend from network IP:**

```powershell
# Replace with your actual IP
curl http://192.168.1.100:8000/health
```

If this fails, the issue is with network binding or firewall.

#### 2. Check Windows Firewall

**Option A: Temporarily disable for testing (NOT RECOMMENDED for production)**

```powershell
# Disable Windows Firewall (Private network only)
Set-NetFirewallProfile -Profile Private -Enabled False
```

**Option B: Add firewall rule (RECOMMENDED)**

```powershell
# Add rule for Python (backend)
New-NetFirewallRule -DisplayName "StoryCraft Backend" -Direction Inbound -Program "C:\Python\python.exe" -Action Allow

# Or allow port 8000 specifically
New-NetFirewallRule -DisplayName "StoryCraft Backend Port" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Add rule for Node (frontend)
New-NetFirewallRule -DisplayName "StoryCraft Frontend Port" -Direction Inbound -Protocol TCP -LocalPort 3001 -Action Allow
```

**Check existing firewall rules:**

```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*StoryCraft*"}
```

#### 3. Verify Network Configuration

**Get your PC's IP address:**

```powershell
# Get WiFi IP
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*Wi-Fi*"}).IPAddress

# Or check all IPs
ipconfig | Select-String "IPv4"
```

**Verify both devices on same network:**

- PC WiFi: 192.168.x.x
- Mobile WiFi: 192.168.x.y (same subnet)

#### 4. Test from Mobile Device Browser

**Open Chrome on mobile and navigate to:**

1. `http://192.168.x.x:8000/health` - Backend health check
2. `http://192.168.x.x:8000/api/characters` - API endpoint
3. `http://192.168.x.x:3001/` - Frontend app

**Check browser console:**

- Open Chrome DevTools via USB debugging
- Look for `[API Config] Using API URL:` message
- Check for CORS errors or network timeouts

#### 5. Backend Server Verification

**Check if backend is bound to correct interface:**

```powershell
# Should show 0.0.0.0:8000 (all interfaces)
netstat -an | Select-String "8000"
```

If it shows `127.0.0.1:8000`, the backend is only listening on localhost.

**Fix: Restart backend with correct host:**

```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 6. Frontend API Configuration

**Check API config logs:**
The Characters page now logs the API URL being used:

```
[Characters] Checking API health at: http://192.168.x.x:8000/health
[Characters] API health check: {status: "healthy"}
[Characters] Loading from API URL: http://192.168.x.x:8000
```

If you see errors here, note the specific error message.

### Common Issues and Solutions

#### Issue: "Cannot reach backend API"

**Solution:** Backend server not running or not accessible on network

- Start backend: `npm run dev:backend` or `cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Add firewall rule (see step 2 above)

#### Issue: "Network Error" or "ERR_CONNECTION_REFUSED"

**Solution:** Firewall blocking port 8000

- Add firewall rule for port 8000
- Or temporarily disable firewall to test

#### Issue: "CORS Error"

**Solution:** CORS not configured for your IP

- Backend main.py already has `allow_origins=["*"]` which should work
- Check if backend needs restart after changing CORS config

#### Issue: Works on localhost but not on 192.168.x.x

**Solution:** Backend bound to 127.0.0.1 instead of 0.0.0.0

- Verify: `netstat -an | Select-String "8000"`
- Fix: Start backend with `--host 0.0.0.0`

#### Issue: Timeout after 10 seconds

**Solution:** Network latency or backend slow to respond

- Check backend logs for errors
- Increase timeout in Characters.jsx (currently 10 seconds)
- Check if backend is hanging on database queries

### Testing Checklist

- [ ] Backend running on 0.0.0.0:8000 (not 127.0.0.1)
- [ ] `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] `curl http://192.168.x.x:8000/health` returns `{"status": "healthy"}`
- [ ] Windows Firewall rule added for port 8000
- [ ] Mobile device on same WiFi network as PC
- [ ] Frontend shows correct API URL in console logs
- [ ] Mobile browser can access `http://192.168.x.x:8000/health`
- [ ] Mobile browser can access `http://192.168.x.x:3001/`

### Enhanced Debugging (Added to Characters.jsx)

The Characters page now includes:

1. **API Health Check** - Tests backend connectivity before loading data
2. **Detailed Error Messages** - Shows API URL and troubleshooting steps
3. **Console Logging** - All API calls logged for debugging
4. **Timeout Configuration** - 10 second timeout with clear error messages

### Quick Fix Commands

**Restart both servers with network access:**

```powershell
# Kill existing servers
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Stop-Process -Name node -Force -ErrorAction SilentlyContinue

# Start backend
cd backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

# Start frontend
cd ..\frontend
npm run dev
```

**Add firewall rules (run as Administrator):**

```powershell
# Backend
New-NetFirewallRule -DisplayName "StoryCraft Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Frontend
New-NetFirewallRule -DisplayName "StoryCraft Frontend" -Direction Inbound -Protocol TCP -LocalPort 3001 -Action Allow
```

### Still Not Working?

If characters still don't load after following all steps:

1. **Capture network traffic:**

   - Open Chrome DevTools on mobile (USB debugging)
   - Go to Network tab
   - Try loading Characters page
   - Share screenshot of failed requests

2. **Check backend logs:**

   - Look at backend terminal for incoming requests
   - Should see: `INFO:     192.168.x.y:xxxx - "GET /api/characters HTTP/1.1" 200 OK`
   - If no requests appear, issue is network/firewall

3. **Test with curl from another device:**

   ```bash
   # From another computer on same network
   curl http://192.168.x.x:8000/api/characters
   ```

4. **Verify CORS headers:**
   ```powershell
   curl -I http://192.168.x.x:8000/api/characters
   # Should include: Access-Control-Allow-Origin: *
   ```

### Next Steps

After fixing the issue, test:

1. Navigate to Characters page from mobile
2. Should see characters load (or "No Characters Yet" message)
3. Console should show successful API calls
4. No error alerts should appear

Report back with:

- Error message from Characters page (if any)
- Console logs from mobile browser
- Backend terminal output
- Results of firewall/network tests
