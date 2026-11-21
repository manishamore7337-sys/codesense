import sqlite3

DB_NAME = "codesense.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            syntax_status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_analysis(code, syntax_status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO analysis_history (code, syntax_status)
        VALUES (?, ?)
        """,
        (code, syntax_status)
    )

    conn.commit()
    conn.close()
def get_analysis_history():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""

        SELECT id, code, syntax_status, created_at
        FROM analysis_history
        ORDER BY id DESC
    """)

        records = cursor.fetchall()
        conn.close()

        return records
if __name__ == "__main__":
    create_database()
    print("Database and table created successfully!")
    history = get_analysis_history()

    print("\nanalysis history:")
    for record in history:
        print(record)
    
    