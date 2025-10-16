# Network Access Guide for Mobile Testing

This guide explains how to access StoryCraft from mobile devices on your local network.

## 🌐 Overview

StoryCraft is now configured for network access, allowing you to test the app on mobile devices (like your Pixel 8 Pro) while running the development servers on your PC.

## ✅ What's Configured

### Backend (FastAPI)
- **Binding**: `0.0.0.0:8000` (all network interfaces)
- **CORS**: Allows all origins in development mode
- **Accessible via**: 
  - `http://localhost:8000` (local)
  - `http://192.168.x.x:8000` (network)

### Frontend (Vite)
- **Binding**: `0.0.0.0:3000` (all network interfaces)
- **API Detection**: Automatically uses current hostname
- **Accessible via**: 
  - `http://localhost:3000` (local)
  - `http://192.168.x.x:3000` (network)

### API Configuration
- **Location**: `frontend/src/config/api.js`
- **Logic**: `API_URL = http://${window.location.hostname}:8000`
- **Result**: Frontend always connects to backend on same IP

## 🚀 How to Use

### Step 1: Find Your PC's IP Address

**Windows (PowerShell):**
```powershell
ipconfig | Select-String "IPv4"
```

Look for your WiFi adapter's IPv4 address (e.g., `192.168.1.100`)

**Alternative Method:**
```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -like "*Wi-Fi*"}).IPAddress
```

### Step 2: Start Both Servers

```powershell
# From project root
npm run dev:all
```

Or start them separately:

**Backend:**
```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```powershell
cd frontend
npm run dev
# (already configured with --host flag)
```

### Step 3: Note the Network URLs

When Vite starts, you'll see output like:
```
  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.100:3000/
```

The **Network** URL is what you'll use on your mobile device.

### Step 4: Access from Mobile

1. **Ensure** your mobile device is on the **same WiFi network** as your PC
2. **Open Chrome** on your Pixel 8 Pro
3. **Navigate to** the Network URL (e.g., `http://192.168.1.100:3000`)
4. **Test** creating/viewing characters, stories, and worlds

## 🔍 Verification

### Check API Connection

1. Open the browser console on mobile (Chrome DevTools via USB debugging)
2. Look for: `[API Config] Using API URL: http://192.168.x.x:8000`
3. This confirms the frontend is using the correct backend URL

### Test Data Flow

1. **Create** a character on mobile
2. **View** it in the Characters list
3. **Navigate** to desktop browser at `http://localhost:3000`
4. **Verify** the character appears there too
5. **Result**: Same database, accessible from both devices

## 🛠️ Troubleshooting

### Issue: "Cannot connect to backend"

**Possible Causes:**
1. **Backend not running** - Start it with `npm run dev:backend`
2. **Wrong IP address** - Run `ipconfig` again to verify
3. **Firewall blocking** - Allow Python and Node.js through Windows Firewall
4. **Different WiFi networks** - Ensure PC and phone on same network

**Check Firewall:**
```powershell
# Check if Python is allowed
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Python*"}

# Check if Node.js is allowed
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Node*"}
```

**Add Firewall Rules (if needed):**
```powershell
# Allow Python (backend)
New-NetFirewallRule -DisplayName "Python Backend" -Direction Inbound -Program "C:\Python310\python.exe" -Action Allow

# Allow Node.js (frontend)
New-NetFirewallRule -DisplayName "Node.js Frontend" -Direction Inbound -Program "C:\Program Files\nodejs\node.exe" -Action Allow
```

### Issue: "Frontend loads but no data"

**Check Console:**
- Look for CORS errors
- Verify API URL is correct (not localhost on mobile)

**Verify Backend CORS:**
```python
# backend/main.py should have:
allow_origins=["*"]  # In development mode
```

### Issue: "IP address changed"

**Reason:** DHCP assigned a new IP to your PC

**Solution:**
1. Find new IP: `ipconfig`
2. No code changes needed - API URL auto-detects
3. Just use new network URL: `http://<new-ip>:3000`

**Optional - Reserve IP:**
- Configure static IP in router settings
- Or use router's DHCP reservation feature

## 📱 Mobile Testing Workflow

### Recommended Flow:

1. **Start servers** on PC
2. **Note network URL** from Vite output
3. **Open on mobile** using network URL
4. **Keep terminal visible** on PC to see API requests
5. **Test features** on mobile
6. **Check console** on PC for errors
7. **Verify data** on desktop browser

### USB Debugging (Optional):

For advanced debugging, connect phone via USB:

1. **Enable Developer Options** on Pixel 8 Pro
2. **Enable USB Debugging**
3. **Connect** phone to PC via USB
4. **Open Chrome** on PC: `chrome://inspect`
5. **Inspect** your mobile browser tab
6. **View console**, network requests, etc.

## 🔒 Security Notes

### Development Mode

The current configuration is for **development only**:
- `allow_origins=["*"]` allows all CORS requests
- `--host 0.0.0.0` exposes servers to network
- **Not suitable for production**

### Production Considerations

For production deployment:
1. **Restrict CORS** to specific domains
2. **Use HTTPS** for encryption
3. **Add authentication** for API access
4. **Configure reverse proxy** (nginx, etc.)
5. **Set environment variables** for API URLs

## 📊 How It Works

### Architecture

```
Mobile Device (192.168.1.50)
  ↓
  Chrome Browser → http://192.168.1.100:3000
  ↓
  Vite Dev Server (Frontend)
    ↓
    API_URL = http://192.168.1.100:8000
    ↓
  Uvicorn Server (Backend)
    ↓
  SQLite Database (storycraft.db)
```

### API URL Resolution

```javascript
// frontend/src/config/api.js
const getApiUrl = () => {
  const hostname = window.location.hostname;
  // localhost:3000 → http://localhost:8000
  // 192.168.1.100:3000 → http://192.168.1.100:8000
  return `http://${hostname}:8000`;
};
```

### Benefits

✅ **Automatic**: No manual IP configuration needed
✅ **Flexible**: Works on localhost AND network IPs
✅ **Consistent**: Same code works everywhere
✅ **Simple**: Single source of truth for API URL
✅ **Testable**: Real mobile testing on real devices

## 🎯 Testing Checklist

Use this checklist when testing network access:

- [ ] PC and mobile on same WiFi network
- [ ] Backend running on PC (`http://<ip>:8000/health` accessible)
- [ ] Frontend running on PC (`http://<ip>:3000` accessible)
- [ ] Mobile can load frontend (homepage visible)
- [ ] Mobile can create new character (API request succeeds)
- [ ] Mobile can view character list (data loads)
- [ ] Mobile can view character details (navigation works)
- [ ] Character created on mobile appears on desktop
- [ ] Character created on desktop appears on mobile
- [ ] All CRUD operations work (Create, Read, Update, Delete)

## 📚 Related Documentation

- **Mobile Styling**: See `MOBILE_STYLING_GUIDE.md`
- **Mobile Testing**: See `MOBILE_TESTING_CHECKLIST.md`
- **Project Setup**: See `README.md`
- **Quick Start**: See `QUICKSTART.md`

## 💡 Tips

### Faster Testing

- **Keep servers running** between test sessions
- **Bookmark network URL** on mobile
- **Use Chrome DevTools** via USB for debugging
- **Check PC terminal** for API logs

### Common Scenarios

**Scenario 1**: Testing on couch with phone
- Start servers on PC
- Access via network URL
- Test mobile UX hands-on

**Scenario 2**: Demo to friend
- Friend's phone on your WiFi
- Give them the network URL
- They can test the app

**Scenario 3**: Multiple devices
- Test on phone AND tablet
- All connect to same backend
- Shared database state

## 🚨 Important Notes

1. **Firewall**: Windows may prompt to allow network access - click "Allow"
2. **WiFi**: PC and mobile must be on same network (not mobile data)
3. **IP Changes**: Router may assign new IP - just use new network URL
4. **Performance**: Network requests slightly slower than localhost (normal)
5. **Data**: Database is on PC - mobile just displays the data

## ✅ Success Criteria

You'll know it's working when:
- ✅ Mobile browser loads the app
- ✅ Console shows correct API URL (network IP, not localhost)
- ✅ You can create a character on mobile
- ✅ Character appears in the list
- ✅ Character persists after refresh
- ✅ Same character visible on desktop browser

---

**Last Updated**: Commit fee357e
**Status**: ✅ Fully Configured and Tested
