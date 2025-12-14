# ✅ Testing Your EC2-Ready Application

## Quick Verification Steps

Run these commands in your terminal (with venv activated):

### 1. Test Storage Backend
```bash
python test_storage.py
```

**Expected output:**
- Should show "Using local storage backend"
- List your existing knowledge bases
- If you have legacy KBs, it will automatically convert them
- You should see: "✅ Converted and saved KB 'xxx' in new format"

### 2. Start the Application
```bash
uvicorn api.main:app --reload
```

**Expected output:**
- No import errors
- Server starts on http://127.0.0.1:8000

### 3. Test Health Endpoint
Open browser or use curl:
```bash
curl http://localhost:8000/health
```

**Expected:** `{"status":"ok"}`

### 4. Test Chat with Existing KB
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"kb_id\": \"bajajtechnologyservices_com\", \"question\": \"What services do they offer?\"}"
```

**Expected:**
- First time: May see "Converting legacy KB format" message
- Should return answer and sources
- Subsequent calls will be faster (already converted)

### 5. Test New Crawl
```bash
curl -X POST http://localhost:8000/api/crawl \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://example.com\"}"
```

**Expected:**
- Crawls website
- Saves in new format automatically
- Returns success with kb_id

---

## What Changed

✅ **Storage abstraction layer** - Works with local or S3
✅ **Legacy KB support** - Automatically converts old format
✅ **EC2-ready** - Can deploy to AWS with just env vars
✅ **Backward compatible** - All existing KBs will work

---

## Environment Variables

Your `.env` should have:
```env
GROQ_API_KEY=your_key_here
STORAGE_BACKEND=local
```

For EC2 deployment, change to:
```env
GROQ_API_KEY=your_key_here
STORAGE_BACKEND=s3
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
```

---

## Troubleshooting

**If you see "Legacy KB detected" error:**
- The automatic conversion will fix it on first load
- Or re-crawl the website to create fresh KB

**If imports fail:**
- Make sure venv is activated
- Run: `pip install -r requirements.txt`

**If chat fails:**
- Check that GROQ_API_KEY is set in .env
- Verify KB exists: Check `storage/data/` directory

---

## Next Steps for EC2 Deployment

When ready to deploy:

1. Create S3 bucket
2. Launch EC2 instance (t3.medium)
3. SSH and run `ec2-setup.sh`
4. Set `STORAGE_BACKEND=s3` in `.env`
5. Done! 🚀

See full guide: `ec2_deployment_guide.md` in artifacts
