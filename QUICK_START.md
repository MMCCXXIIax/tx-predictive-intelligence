# 🚀 QUICK START - Full Source Docker Build

## ⚡ Fast Track (Copy-Paste Commands)

### **Step 1: Install WSL2 (5 min)**

Open PowerShell as Administrator:

```powershell
wsl --install
```

Restart your computer.

---

### **Step 2: Install Docker in WSL2 (5 min)**

After restart, open WSL2:

```bash
# Update system
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker
sudo service docker start
```

---

### **Step 3: Build Image (30-45 min)**

Open PowerShell:

```powershell
cd "C:\Users\S\TX BACK\tx-predictive-intelligence"
.\build-full-source.bat
```

**Go grab coffee ☕ - this builds PyTorch from source!**

---

### **Step 4: Push to Docker Hub (5 min)**

In WSL2:

```bash
# Login
docker login

# Tag (replace YOUR-USERNAME)
docker tag tx-backend:latest YOUR-USERNAME/tx-backend:latest

# Push
docker push YOUR-USERNAME/tx-backend:latest
```

---

### **Step 5: Deploy to Railway (2 min)**

1. Go to **railway.app**
2. New Project → Deploy from Docker Image
3. Enter: `YOUR-USERNAME/tx-backend:latest`
4. Add PostgreSQL
5. Add environment variables
6. Deploy!

---

## ✅ Done!

**Total time: ~1 hour**

**You now have:**
- ✅ PyTorch built from source
- ✅ 100% functionality
- ✅ Maximum performance
- ✅ Production-ready backend

**Your backend URL:** `https://your-app.railway.app`

**Give this to your frontend team!** 🎉
