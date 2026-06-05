from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
from models import db, Member, Equipment, BorrowRecord, Score, LevelExam, Certificate
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///archery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

LEVEL_THRESHOLDS = {
    '白丁': {'avg_score': 0, 'min_count': 0},
    '初级射手': {'avg_score': 60, 'min_count': 3},
    '中级射手': {'avg_score': 80, 'min_count': 5},
    '高级射手': {'avg_score': 100, 'min_count': 8},
    '精英射手': {'avg_score': 120, 'min_count': 12},
    '大师射手': {'avg_score': 140, 'min_count': 20}
}

with app.app_context():
    db.create_all()
    from seed import seed_data
    seed_data()


def calculate_tech_level(member_id):
    scores = Score.query.filter_by(member_id=member_id).all()
    if not scores:
        return '白丁', 0
    
    avg_score = sum(s.total_score for s in scores) / len(scores)
    count = len(scores)
    
    for level in reversed(list(LEVEL_THRESHOLDS.keys())):
        threshold = LEVEL_THRESHOLDS[level]
        if avg_score >= threshold['avg_score'] and count >= threshold['min_count']:
            return level, round(avg_score, 2)
    
    return '白丁', round(avg_score, 2)


@app.route('/api/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    result = []
    for m in members:
        level, avg = calculate_tech_level(m.id)
        result.append({
            'id': m.id,
            'name': m.name,
            'phone': m.phone,
            'join_date': m.join_date,
            'tech_level': level,
            'avg_score': avg
        })
    return jsonify(result)


@app.route('/api/members', methods=['POST'])
def create_member():
    data = request.json
    member = Member(
        name=data['name'],
        phone=data['phone'],
        join_date=data.get('join_date', date.today().isoformat())
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({'id': member.id, 'message': '创建成功'})


@app.route('/api/equipment', methods=['GET'])
def get_equipment():
    equipments = Equipment.query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'type': e.type,
        'serial_number': e.serial_number,
        'brand': e.brand,
        'status': e.status,
        'buy_date': e.buy_date
    } for e in equipments])


@app.route('/api/equipment', methods=['POST'])
def create_equipment():
    data = request.json
    equipment = Equipment(
        name=data['name'],
        type=data['type'],
        serial_number=data['serial_number'],
        brand=data.get('brand', ''),
        status=data.get('status', '可用'),
        buy_date=data.get('buy_date', date.today().isoformat())
    )
    db.session.add(equipment)
    db.session.commit()
    return jsonify({'id': equipment.id, 'message': '创建成功'})


@app.route('/api/equipment/<int:id>', methods=['PUT'])
def update_equipment(id):
    data = request.json
    equipment = Equipment.query.get(id)
    if not equipment:
        return jsonify({'message': '器材不存在'}), 404
    equipment.status = data.get('status', equipment.status)
    db.session.commit()
    return jsonify({'message': '更新成功'})


@app.route('/api/borrow-records', methods=['GET'])
def get_borrow_records():
    records = BorrowRecord.query.order_by(BorrowRecord.borrow_time.desc()).all()
    return jsonify([{
        'id': r.id,
        'member_id': r.member_id,
        'member_name': r.member.name if r.member else '未知',
        'equipment_id': r.equipment_id,
        'equipment_name': r.equipment.name if r.equipment else '未知',
        'equipment_serial': r.equipment.serial_number if r.equipment else '',
        'borrow_time': r.borrow_time,
        'expected_return': r.expected_return,
        'actual_return': r.actual_return,
        'status': r.status
    } for r in records])


@app.route('/api/borrow-records', methods=['POST'])
def create_borrow_record():
    data = request.json
    equipment = Equipment.query.get(data['equipment_id'])
    if not equipment:
        return jsonify({'message': '器材不存在'}), 404
    if equipment.status != '可用':
        return jsonify({'message': f'器材当前状态为"{equipment.status}"，无法借用'}), 400
    
    record = BorrowRecord(
        member_id=data['member_id'],
        equipment_id=data['equipment_id'],
        borrow_time=data['borrow_time'],
        expected_return=data['expected_return'],
        status='借用中'
    )
    equipment.status = '借用中'
    db.session.add(record)
    db.session.commit()
    return jsonify({'id': record.id, 'message': '借用成功'})


@app.route('/api/borrow-records/<int:id>/return', methods=['PUT'])
def return_equipment(id):
    record = BorrowRecord.query.get(id)
    if not record:
        return jsonify({'message': '记录不存在'}), 404
    data = request.json
    record.actual_return = data.get('actual_return', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    record.status = '已归还'
    equipment = Equipment.query.get(record.equipment_id)
    if equipment:
        equipment.status = '可用'
    db.session.commit()
    return jsonify({'message': '归还成功'})


@app.route('/api/scores', methods=['GET'])
def get_scores():
    scores = Score.query.order_by(Score.training_date.desc()).all()
    return jsonify([{
        'id': s.id,
        'member_id': s.member_id,
        'member_name': s.member.name if s.member else '未知',
        'target_distance': s.target_distance,
        'bow_type': s.bow_type,
        'arrows_count': s.arrows_count,
        'total_score': s.total_score,
        'avg_per_arrow': round(s.total_score / s.arrows_count, 2) if s.arrows_count > 0 else 0,
        'training_date': s.training_date,
        'notes': s.notes
    } for s in scores])


@app.route('/api/scores', methods=['POST'])
def create_score():
    data = request.json
    arrows_count = data.get('arrows_count', 12)
    total_score = data.get('total_score')
    
    if total_score is None:
        arrow_scores = data.get('arrow_scores', [])
        total_score = sum(arrow_scores)
    
    score = Score(
        member_id=data['member_id'],
        target_distance=data['target_distance'],
        bow_type=data['bow_type'],
        arrows_count=arrows_count,
        total_score=total_score,
        training_date=data.get('training_date', date.today().isoformat()),
        notes=data.get('notes', '')
    )
    db.session.add(score)
    db.session.commit()
    
    level, avg = calculate_tech_level(data['member_id'])
    member = Member.query.get(data['member_id'])
    if member:
        member.tech_level = level
        db.session.commit()
    
    return jsonify({'id': score.id, 'tech_level': level, 'avg_score': avg, 'message': '成绩录入成功'})


@app.route('/api/scores/<int:id>', methods=['DELETE'])
def delete_score(id):
    score = Score.query.get(id)
    if not score:
        return jsonify({'message': '成绩不存在'}), 404
    member_id = score.member_id
    db.session.delete(score)
    db.session.commit()
    
    level, avg = calculate_tech_level(member_id)
    member = Member.query.get(member_id)
    if member:
        member.tech_level = level
        db.session.commit()
    
    return jsonify({'message': '删除成功', 'tech_level': level, 'avg_score': avg})


@app.route('/api/level-exams', methods=['GET'])
def get_level_exams():
    exams = LevelExam.query.order_by(LevelExam.exam_date.desc()).all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'target_level': e.target_level,
        'exam_date': e.exam_date,
        'exam_location': e.exam_location,
        'pass_score': e.pass_score,
        'status': e.status
    } for e in exams])


@app.route('/api/level-exams', methods=['POST'])
def create_level_exam():
    data = request.json
    exam = LevelExam(
        name=data['name'],
        target_level=data['target_level'],
        exam_date=data['exam_date'],
        exam_location=data.get('exam_location', ''),
        pass_score=data.get('pass_score', 100),
        status=data.get('status', '报名中')
    )
    db.session.add(exam)
    db.session.commit()
    return jsonify({'id': exam.id, 'message': '考试创建成功'})


@app.route('/api/certificates', methods=['GET'])
def get_certificates():
    certs = Certificate.query.order_by(Certificate.issue_date.desc()).all()
    return jsonify([{
        'id': c.id,
        'member_id': c.member_id,
        'member_name': c.member.name if c.member else '未知',
        'exam_id': c.exam_id,
        'exam_name': c.exam.name if c.exam else '未知',
        'level': c.level,
        'score': c.score,
        'issue_date': c.issue_date,
        'certificate_number': c.certificate_number
    } for c in certs])


@app.route('/api/certificates', methods=['POST'])
def create_certificate():
    data = request.json
    import uuid
    cert = Certificate(
        member_id=data['member_id'],
        exam_id=data['exam_id'],
        level=data['level'],
        score=data['score'],
        issue_date=data.get('issue_date', date.today().isoformat()),
        certificate_number=f"ARCH-{date.today().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    )
    db.session.add(cert)
    db.session.commit()
    return jsonify({'id': cert.id, 'certificate_number': cert.certificate_number, 'message': '证书颁发成功'})


@app.route('/api/statistics/equipment-usage', methods=['GET'])
def get_equipment_usage():
    from sqlalchemy import func
    records = BorrowRecord.query.with_entities(
        BorrowRecord.equipment_id,
        func.count(BorrowRecord.id).label('usage_count')
    ).group_by(BorrowRecord.equipment_id).all()
    
    result = []
    for eq_id, count in records:
        eq = Equipment.query.get(eq_id)
        if eq:
            result.append({
                'equipment_id': eq_id,
                'name': eq.name,
                'serial_number': eq.serial_number,
                'type': eq.type,
                'usage_count': count
            })
    result.sort(key=lambda x: x['usage_count'], reverse=True)
    return jsonify(result)


@app.route('/api/statistics/level-distribution', methods=['GET'])
def get_level_distribution():
    members = Member.query.all()
    distribution = {}
    for m in members:
        level, _ = calculate_tech_level(m.id)
        distribution[level] = distribution.get(level, 0) + 1
    
    result = [{'level': k, 'count': v} for k, v in distribution.items()]
    levels_order = ['白丁', '初级射手', '中级射手', '高级射手', '精英射手', '大师射手']
    result.sort(key=lambda x: levels_order.index(x['level']))
    return jsonify(result)


@app.route('/api/statistics/progress/<int:member_id>', methods=['GET'])
def get_member_progress(member_id):
    scores = Score.query.filter_by(member_id=member_id).order_by(Score.training_date).all()
    result = []
    for i, s in enumerate(scores):
        avg_score = sum(sc.total_score for sc in scores[:i+1]) / (i+1)
        result.append({
            'date': s.training_date,
            'score': s.total_score,
            'avg_score': round(avg_score, 2),
            'distance': s.target_distance
        })
    return jsonify(result)


@app.route('/api/statistics/distance-popularity', methods=['GET'])
def get_distance_popularity():
    from sqlalchemy import func
    scores = Score.query.with_entities(
        Score.target_distance,
        func.count(Score.id).label('count'),
        func.avg(Score.total_score).label('avg_score')
    ).group_by(Score.target_distance).all()
    
    result = [{
        'distance': s.target_distance,
        'count': s.count,
        'avg_score': round(s.avg_score, 2)
    } for s in scores]
    result.sort(key=lambda x: x['count'], reverse=True)
    return jsonify(result)


@app.route('/api/statistics/overview', methods=['GET'])
def get_overview():
    member_count = Member.query.count()
    equipment_count = Equipment.query.count()
    borrowed_count = BorrowRecord.query.filter_by(status='借用中').count()
    score_count = Score.query.count()
    cert_count = Certificate.query.count()
    
    return jsonify({
        'member_count': member_count,
        'equipment_count': equipment_count,
        'borrowed_count': borrowed_count,
        'score_count': score_count,
        'cert_count': cert_count
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9502, debug=True)
