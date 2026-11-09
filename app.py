# =====================================================================
#  เซิร์ฟเวอร์ฐานข้อมูล SQLite สำหรับเว็บ my-db-site (IT234)
#  ใช้กับ PythonAnywhere: อยู่ในโฟลเดอร์เดียวกับ index.html (เช่น /home/<ชื่อผู้ใช้>/my-database)
#  repo เดียวกันนี้ขึ้น GitHub Pages ได้ด้วย (GitHub Pages จะไม่รันไฟล์นี้ แค่เก็บไว้เฉย ๆ)
#
#  หน้าที่ของไฟล์นี้:
#    - ส่งหน้าเว็บ (index.html) ให้คนที่เปิดเว็บ
#    - ส่งไฟล์ฐานข้อมูลให้เบราว์เซอร์อ่าน (SELECT ทำในเบราว์เซอร์)
#    - รับคำสั่ง INSERT / UPDATE / DELETE แล้วบันทึกลงไฟล์ database.db จริง
# =====================================================================

import os
import re
import sqlite3
import threading

from flask import Flask, Response, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "database.db")

# อนุญาตเฉพาะคำสั่งที่เพิ่ม แก้ หรือลบข้อมูล
# ห้ามคำสั่งที่เปลี่ยนโครงสร้าง (CREATE, DROP, ALTER ...) เพราะใครก็เปิดเว็บนี้ได้
ALLOWED = re.compile(r"^\s*(INSERT|UPDATE|DELETE|REPLACE)\b", re.IGNORECASE)
BLOCKED = re.compile(r"\b(ATTACH|DETACH|PRAGMA|VACUUM|load_extension)\b", re.IGNORECASE)

app = Flask(__name__, static_folder=None)
lock = threading.Lock()


def connect():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.execute("PRAGMA foreign_keys = ON")   # ให้ SQLite ตรวจ FOREIGN KEY ทุกครั้ง
    return con


def db_version():
    st = os.stat(DB_PATH)
    return "%d-%d" % (st.st_mtime_ns, st.st_size)


def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ---------- หน้าเว็บ ----------
@app.route("/")
def home():
    return no_cache(send_from_directory(BASE, "index.html"))


@app.route("/site.json")
def site_json():
    if not os.path.exists(os.path.join(BASE, "site.json")):
        return jsonify({}), 404
    return no_cache(send_from_directory(BASE, "site.json"))


# ---------- API ----------
@app.route("/api/info")
def info():
    return no_cache(jsonify({"mode": "server"}))


@app.route("/api/version")
def version():
    return no_cache(jsonify({"version": db_version()}))


@app.route("/api/db")
def get_db():
    # คัดลอกฐานข้อมูลทั้งไฟล์แบบปลอดภัย แล้วส่งให้เบราว์เซอร์อ่านด้วย SQL
    with lock:
        src = connect()
        mem = sqlite3.connect(":memory:")
        src.backup(mem)
        src.close()
        tmp = os.path.join(BASE, ".snapshot.db")
        out = sqlite3.connect(tmp)
        mem.backup(out)
        out.close()
        mem.close()
        with open(tmp, "rb") as f:
            data = f.read()
        os.remove(tmp)
        ver = db_version()
    resp = Response(data, mimetype="application/x-sqlite3")
    resp.headers["X-DB-Version"] = ver
    return no_cache(resp)


@app.route("/api/exec", methods=["POST"])
def exec_sql():
    body = request.get_json(silent=True) or {}
    sql = str(body.get("sql", "")).strip()
    params = body.get("params") or []

    if not ALLOWED.match(sql):
        return jsonify(ok=False, error="อนุญาตเฉพาะคำสั่ง INSERT, UPDATE, DELETE"), 400
    if BLOCKED.search(sql):
        return jsonify(ok=False, error="คำสั่งนี้ไม่อนุญาตบนเว็บที่ใช้งานจริง"), 400
    if not isinstance(params, list) or len(params) > 200:
        return jsonify(ok=False, error="ข้อมูลที่ส่งมาไม่ถูกต้อง"), 400
    if len(sql) > 5000:
        return jsonify(ok=False, error="คำสั่งยาวเกินไป"), 400

    with lock:
        con = connect()
        try:
            # ส่งค่าเป็น parameter (?) แยกจากคำสั่ง กัน SQL Injection
            cur = con.execute(sql, params)
            con.commit()
            result = dict(ok=True, changes=cur.rowcount, lastrowid=cur.lastrowid)
        except sqlite3.Error as e:          # เช่น UNIQUE, NOT NULL, FOREIGN KEY constraint failed
            con.rollback()
            return jsonify(ok=False, error=str(e)), 400
        except Exception as e:
            con.rollback()
            return jsonify(ok=False, error=str(e)), 400
        finally:
            con.close()
        result["version"] = db_version()
    return no_cache(jsonify(result))


if __name__ == "__main__":
    # ทดลองรันในเครื่อง: python flask_app.py แล้วเปิด http://localhost:5000
    app.run(debug=True)
