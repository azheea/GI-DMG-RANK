from flask import Flask, render_template, request
import sqlite3
import threading
import getDamage
import getAllavatars

app = Flask(__name__)

# 创建数据库连接
conn = threading.local()
allAvatar = getAllavatars.read_text_file()
print(allAvatar)
def get_db():
    db = getattr(conn, 'db', None)  # 使用getattr函数获取conn对象中的db属性，如果不存在则返回None
    if db is None:
        db = conn.db = sqlite3.connect('rank.db')
        db.execute("PRAGMA foreign_keys = 1")  # 开启外键约束
        db.row_factory = sqlite3.Row  # 使用Row工厂，使查询结果可以通过列名访问
    return db

def close_db(error=None):
    db = getattr(conn, 'db', None)
    if db is not None:
        db.close()
        conn.db = None

# 创建rank表
def init_db():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS rank
                     (user_id TEXT PRIMARY KEY, damage_num INTEGER, avatar INTEGER, rank INTEGER)''')
        db.commit()

@app.teardown_appcontext
def teardown_db(error=None):
    close_db()

# 主页路由，展示排名
@app.route('/')
def index():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('SELECT avatar, user_id, damage_num, rank FROM rank WHERE rank <= 50 ORDER BY damage_num DESC')
        ranked_data = c.fetchall()
        ranked_data = [dict(row) for row in ranked_data]  # 将每行数据转换为字典形式
        for i in ranked_data:
            i["avatar"] = allAvatar[str(i["avatar"])]
    return render_template('index.html', data=ranked_data)

@app.route('/api', methods=['POST'])
def submit():
    user_id = request.form.get('user_id')
    if len(str(user_id)) != 9 or not user_id.isdigit():
        return "无效的uid"
    damage_num = getDamage.get(int(user_id))
    if damage_num[2] == 1:
        return render_template('submitdone.html', return_word="无效的UID,请检查后重试")
    damageAvatar = damage_num[1]
    damage_num = damage_num[0]
    
    if isinstance(damage_num, int):
        with app.app_context():
            db = get_db()
            c = db.cursor()
            # 检查是否存在相同的user_id
            c.execute('SELECT user_id FROM rank WHERE user_id = ?', (user_id,))
            existing_user = c.fetchone()
            if existing_user is not None:
                # 更新数据
                c.execute('UPDATE rank SET damage_num = ? WHERE user_id = ? WHERE avatar = ?', (damage_num, user_id ,damageAvatar))
            else:
                # 插入新数据
                c.execute('INSERT INTO rank (user_id, damage_num, avatar) VALUES (?, ?, ?)', (user_id, damage_num ,damageAvatar))
            # 更新排名
            c.execute('WITH ranked_data AS (SELECT user_id, damage_num, avatar,RANK() OVER (ORDER BY damage_num DESC) AS rank FROM rank) '
                      'UPDATE rank SET rank = (SELECT rank FROM ranked_data WHERE ranked_data.user_id = rank.user_id)')
            db.commit()
        print(f"{user_id} 提交了数据,他的返回值为{damage_num}")
        return render_template('submitdone.html', return_word=f'您的伤害是{damage_num}提交成功 快去主页看看吧')
    else:
        return render_template('submitdone.html', return_word=damage_num[1])

@app.route('/adminbg')
def admin():
    pass

@app.route('/submit')
def submit_():
    return render_template('submit.html')

if __name__ == '__main__':
    init_db()
    app.run()