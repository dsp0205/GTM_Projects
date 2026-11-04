CREATE TABLE IF NOT EXISTS accounts (
  account_id INTEGER PRIMARY KEY,
  domain TEXT NOT NULL,
  employees INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS signups (
  signup_id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES accounts(account_id),
  created_at TEXT NOT NULL,
  hdyhau_text TEXT
);
CREATE TABLE IF NOT EXISTS coded_answers (
  signup_id INTEGER PRIMARY KEY REFERENCES signups(signup_id),
  channel TEXT NOT NULL,
  named_source TEXT NOT NULL,
  confidence TEXT NOT NULL,
  prompt_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS opportunities (
  opp_id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES accounts(account_id),
  created_at TEXT NOT NULL,
  amount_usd REAL NOT NULL
);
