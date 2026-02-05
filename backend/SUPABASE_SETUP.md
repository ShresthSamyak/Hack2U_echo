# Supabase Setup Guide

## 📋 Quick Setup (5 minutes)

### Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email

### Step 2: Create New Project
1. Click "New Project"
2. Fill in details:
   - **Name**: product-intelligence-agent
   - **Database Password**: (generate a strong one, save it!)
   - **Region**: Choose closest to your users (e.g., US East)
3. Click "Create new project"
4. Wait 2-3 minutes for provisioning

### Step 3: Run SQL Schema
1. In Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click "New query"
3. Copy the **entire SQL schema** from `database_schema.md`
4. Paste into the editor
5. Click "Run" (or press Ctrl+Enter)
6. You should see "Success. No rows returned"

### Step 4: Get API Credentials
1. Go to **Settings** → **API** (left sidebar)
2. Copy these values:

```
Project URL: https://xxxxx.supabase.co
```

```
anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

```
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

⚠️ **IMPORTANT**: Use `service_role` key for backend (full access)

### Step 5: Update .env File
Open `backend/.env` and add:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 6: Create Test Brand
Run this in Supabase **SQL Editor**:

```sql
INSERT INTO brands (name, api_key, settings)
VALUES (
    'TechHome',
    'test_' || gen_random_uuid()::text,
    '{"brand_name": "TechHome", "default_mode": "PRE_PURCHASE"}'::jsonb
)
RETURNING id, api_key;
```

Copy the returned `id` and add to `.env`:
```bash
DEFAULT_BRAND_ID=xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx
```

### Step 7: Test Connection
Restart your backend:
```bash
python backend/main.py
```

Look for:
```
✅ Supabase database connected!
```

### Step 8: Test Conversation Storage
In Postman, send a chat message. Then check Supabase:
1. Go to **Table Editor** → **conversations**
2. You should see a new row with your session_id and messages!

---

## 🔍 Viewing Data in Supabase

### Conversations Table
- **Table Editor** → conversations
- See all chat sessions, messages, timestamps

### Analytics Table  
- **Table Editor** → analytics
- See all queries, response times, errors

### Run Queries
- **SQL Editor** → New query
- Example: Get all conversations from last 24h
```sql
SELECT * FROM conversations
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

---

## ⚠️ Troubleshooting

### "Database features disabled"
- Check SUPABASE_URL and SUPABASE_SERVICE_KEY in .env
- Make sure no extra spaces or quotes

### "relation does not exist"
- Run SQL schema again (Step 3)
- Make sure you're in the correct project

### "JWT expired" or "Invalid API key"
- Regenerate keys in Settings → API
- Update .env file

---

## 🎯 Next Steps

Once setup is complete:
1. ✅ Database is connected
2. ✅ Conversations are being stored
3. ✅ Analytics are being logged
4. 🔄 Agent will use database instead of RAM
5. 🚀 Ready for deployment!
