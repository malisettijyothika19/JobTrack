from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("jobtrack.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = sqlite3.connect("jobtrack.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            job_url TEXT,
            status TEXT NOT NULL,
            application_date TEXT NOT NULL
        )
    """)

    try:
        conn.execute("ALTER TABLE jobs ADD COLUMN job_url TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = get_db_connection()

    jobs = conn.execute("SELECT * FROM jobs").fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    applied = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status = 'Applied'"
    ).fetchone()[0]

    interview = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status = 'Interview'"
    ).fetchone()[0]

    selected = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status = 'Selected'"
    ).fetchone()[0]

    rejected = conn.execute(
        "SELECT COUNT(*) FROM jobs WHERE status = 'Rejected'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        jobs=jobs,
        total=total,
        applied=applied,
        interview=interview,
        selected=selected,
        rejected=rejected
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        company = request.form["company"]
        position = request.form["position"]
        job_url=request.form["job_url"]
        status = request.form["status"]
        application_date = request.form["application_date"]
        
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO jobs (company, position, job_url, status, application_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company, position, job_url, status, application_date)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()

    if request.method == "POST":
        company = request.form["company"]
        position = request.form["position"]
        job_url=request.form["job_url"]
        status = request.form["status"]
        application_date = request.form["application_date"]

        conn.execute(
            """
            UPDATE jobs
            SET company = ?, position = ?, job_url = ?, status = ?, application_date = ?
            WHERE id = ?
            """,
            (company, position, job_url, status, application_date, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    job = conn.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template("edit.html", job=job)


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM jobs WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

init_db()
if __name__ == "__main__":
    app.run(debug=True)