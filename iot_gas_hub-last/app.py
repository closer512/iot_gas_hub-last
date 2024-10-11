from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_migrate import Migrate

app = Flask(__name__, static_url_path='/static')

# 使用 SQLite 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iot_gas_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # 用于 flash 消息提示
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# 定义数据模型
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    email_address = db.Column(db.String(256), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    gas_type = db.Column(db.String(256), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    gas_level = db.Column(db.Float, nullable=False)
    gas_data = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# 主页
@app.route('/')
def index():
    return render_template('index.html')
# 实时获取趋势图数据
@app.route('/api/trend')
def get_trend_data():
    # 按时间降序获取最新的10条数据
    data = SensorData.query.order_by(SensorData.time.desc()).limit(10).all()

    # 因为前端要按照时间升序显示，所以我们需要将数据反转
    data.reverse()

    trend_data = {
        "times": [entry.time.strftime('%Y-%m-%d %H:%M:%S') for entry in data],
        "gas_levels": [entry.gas_level for entry in data]
    }
    return jsonify(trend_data)


# 获取最新的警报数据
@app.route('/api/alerts')
def get_alerts_data():
    # 获取最新的10条警报
    alerts = SensorData.query.order_by(SensorData.time.desc()).limit(10).all()
    
    alerts_data = [{
        "sensor_id": entry.sensor_id,
        "time": entry.time.strftime('%Y-%m-%d %H:%M:%S'),
        "address": entry.address,
        "gas_level": entry.gas_level
    } for entry in alerts]
    
    return jsonify(alerts_data)

# 获取仪表盘的实时数据
@app.route('/api/gas-level')
def get_current_gas_level():
    # 获取最新的一条数据
    latest_data = SensorData.query.order_by(SensorData.time.desc()).first()
    
    if latest_data:
        gas_data = {
            "gas_level": latest_data.gas_level,
            "status": "Normal" if latest_data.gas_level < 50 else "Warning"
        }
    else:
        gas_data = {"gas_level": 0, "status": "No Data"}
    
    return jsonify(gas_data)

# 获取Peak Gas Levels数据
@app.route('/api/peak-gas-levels')
def get_peak_gas_levels():
    today = datetime.date.today()
    start_month = today.replace(day=1)
    
    # 查询今天的峰值
    today_peak = db.session.query(db.func.max(SensorData.gas_level)).filter(db.func.date(SensorData.time) == today).scalar()
    
    # 查询本月的峰值
    month_peak = db.session.query(db.func.max(SensorData.gas_level)).filter(SensorData.time >= start_month).scalar()
    
    # 查询历史最高峰值
    history_peak = db.session.query(db.func.max(SensorData.gas_level)).scalar()
    
    peak_data = {
        "today": today_peak if today_peak else 0,
        "month": month_peak if month_peak else 0,
        "history": history_peak if history_peak else 0
    }
    
    return jsonify(peak_data)

# 添加数据
@app.route('/add', methods=['POST'])
def add_data():
    try:
        sensor_id = request.form['sensor_id']
        address = request.form['address']
        email_address = request.form['email_address']
        contact_number = request.form['contact_number']
        gas_type = request.form['gas_type']
        time = request.form['time']
        gas_level = float(request.form['gas_level'])
        gas_data = request.form['gas_data']

        # 创建一个新条目，保存数据到数据库
        new_data = SensorData(
            sensor_id=sensor_id,
            address=address,
            email_address=email_address,
            contact_number=contact_number,
            gas_type=gas_type,
            time=datetime.datetime.fromisoformat(time),
            gas_level=gas_level,
            gas_data=gas_data
        )

        db.session.add(new_data)
        db.session.commit()
        flash('Data added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding data: {str(e)}', 'danger')

    return redirect(url_for('index'))

# 编辑数据
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    entry = SensorData.query.get_or_404(id)
    if request.method == 'POST':
        try:
            entry.sensor_id = request.form['sensor_id']
            entry.address = request.form['address']
            entry.email_address = request.form['email_address']
            entry.contact_number = request.form['contact_number']
            entry.gas_type = request.form['gas_type']
            entry.time = datetime.datetime.fromisoformat(request.form['time'])
            entry.gas_level = float(request.form['gas_level'])
            entry.gas_data = request.form['gas_data']
            db.session.commit()
            flash('Data updated successfully!', 'success')
            return redirect(url_for('alerts'))
        except Exception as e:
            flash(f'Error updating data: {str(e)}', 'danger')
    return render_template('edit.html', entry=entry)

# 删除数据
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    entry = SensorData.query.get_or_404(id)
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Data deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting data: {str(e)}', 'danger')
    return redirect(url_for('alerts'))

@app.route('/alerts', methods=['GET'])
def alerts():
    # 获取查询参数
    sensor_id = request.args.get('sensor_id')
    address = request.args.get('address')
    email_address = request.args.get('email_address')
    contact_number = request.args.get('contact_number')
    gas_type = request.args.get('gas_type')
    time = request.args.get('time')
    gas_level = request.args.get('gas_level')
    gas_data = request.args.get('gas_data')

    # 构建查询
    query = SensorData.query

    if sensor_id:
        query = query.filter(SensorData.sensor_id.like(f"%{sensor_id}%"))
    if address:
        query = query.filter(SensorData.address.like(f"%{address}%"))
    if email_address:
        query = query.filter(SensorData.email_address.like(f"%{email_address}%"))
    if contact_number:
        query = query.filter(SensorData.contact_number.like(f"%{contact_number}%"))
    if gas_type:
        query = query.filter(SensorData.gas_type.like(f"%{gas_type}%"))
    if time:
        # 假设时间是精确匹配，如果需要模糊匹配可以进行转换
        query = query.filter(SensorData.time == time)
    if gas_level:
        query = query.filter(SensorData.gas_level == float(gas_level))
    if gas_data:
        query = query.filter(SensorData.gas_data.like(f"%{gas_data}%"))

    # 执行查询
    alert_data = query.all()

    # 渲染模板并传递查询结果
    return render_template('alerts.html', alert_data=alert_data)

@app.route('/alerts')
def alerts_page():
    return render_template('alerts.html')



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5001, debug=True)
