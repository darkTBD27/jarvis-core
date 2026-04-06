CREATE TABLE IF NOT EXISTS conversations (

id SERIAL PRIMARY KEY,

user_id TEXT,

message TEXT,

response TEXT,

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
