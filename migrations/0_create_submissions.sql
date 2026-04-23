CREATE TABLE IF NOT EXISTS submissions (
    submission_id TEXT PRIMARY KEY,
    submitted_at TEXT NOT NULL,
    country TEXT NOT NULL,
    company_size TEXT NOT NULL,
    answers TEXT NOT NULL
);
