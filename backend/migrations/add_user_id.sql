-- Add user_id column to conversations table for product-scoped memory
-- Run this in Supabase SQL Editor

-- Add user_id column (references auth.users table)
ALTER TABLE conversations ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Add indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_conversations_user_product 
ON conversations(user_id, model_id, mode);

CREATE INDEX IF NOT EXISTS idx_conversations_user 
ON conversations(user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_created 
ON conversations(created_at DESC);

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'conversations';
