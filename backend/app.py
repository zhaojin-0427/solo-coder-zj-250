from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date
from models import db, Member, Equipment, BorrowRecord, Score, LevelExam, Certificate, ExamRegistration, ExamRoundScore, ExamEquipmentReservation
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
        'status': e.status,
        'arrows_per_round': e.arrows_per_round,
        'total_rounds': e.total_rounds,
        'distance_group': e.distance_group,
        'bow_type_restriction': e.bow_type_restriction,
        'registered_count': ExamRegistration.query.filter_by(exam_id=e.id).count(),
        'registration_capacity': e.registration_capacity
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
        status=data.get('status', '报名中'),
        exam_project=data.get('exam_project', '射箭'),
        distance_group=data['distance_group'],
        bow_type_restriction=data.get('bow_type_restriction', ''),
        registration_capacity=data.get('registration_capacity', 50),
        registration_deadline=data['registration_deadline'],
        arrows_per_round=data.get('arrows_per_round', 6),
        total_rounds=data.get('total_rounds', 12)
    )
    db.session.add(exam)
    db.session.commit()
    return jsonify({'id': exam.id, 'message': '考试创建成功'})


@app.route('/api/level-exams/<int:id>', methods=['PUT'])
def update_level_exam(id):
    exam = LevelExam.query.get(id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    data = request.json
    exam.name = data.get('name', exam.name)
    exam.target_level = data.get('target_level', exam.target_level)
    exam.exam_date = data.get('exam_date', exam.exam_date)
    exam.exam_location = data.get('exam_location', exam.exam_location)
    exam.pass_score = data.get('pass_score', exam.pass_score)
    exam.status = data.get('status', exam.status)
    exam.distance_group = data.get('distance_group', exam.distance_group)
    exam.bow_type_restriction = data.get('bow_type_restriction', exam.bow_type_restriction)
    exam.registration_capacity = data.get('registration_capacity', exam.registration_capacity)
    exam.registration_deadline = data.get('registration_deadline', exam.registration_deadline)
    exam.arrows_per_round = data.get('arrows_per_round', exam.arrows_per_round)
    exam.total_rounds = data.get('total_rounds', exam.total_rounds)
    db.session.commit()
    return jsonify({'message': '考试更新成功'})


@app.route('/api/level-exams/<int:id>', methods=['DELETE'])
def delete_level_exam(id):
    exam = LevelExam.query.get(id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    ExamRegistration.query.filter_by(exam_id=id).delete()
    ExamRoundScore.query.filter_by(exam_id=id).delete()
    ExamEquipmentReservation.query.filter_by(exam_id=id).delete()
    Certificate.query.filter_by(exam_id=id).delete()
    db.session.delete(exam)
    db.session.commit()
    return jsonify({'message': '考试删除成功'})


@app.route('/api/level-exams/<int:id>', methods=['GET'])
def get_level_exam_detail(id):
    exam = LevelExam.query.get(id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    registered_count = ExamRegistration.query.filter_by(exam_id=id).count()
    return jsonify({
        'id': exam.id,
        'name': exam.name,
        'target_level': exam.target_level,
        'exam_date': exam.exam_date,
        'exam_location': exam.exam_location,
        'pass_score': exam.pass_score,
        'status': exam.status,
        'exam_project': exam.exam_project,
        'distance_group': exam.distance_group,
        'bow_type_restriction': exam.bow_type_restriction,
        'registration_capacity': exam.registration_capacity,
        'registered_count': registered_count,
        'registration_deadline': exam.registration_deadline,
        'arrows_per_round': exam.arrows_per_round,
        'total_rounds': exam.total_rounds
    })


@app.route('/api/exam-registrations', methods=['GET'])
def get_exam_registrations():
    exam_id = request.args.get('exam_id', type=int)
    query = ExamRegistration.query
    if exam_id:
        query = query.filter_by(exam_id=exam_id)
    registrations = query.order_by(ExamRegistration.registration_time.desc()).all()
    result = []
    for r in registrations:
        bow_type = '反曲弓'
        if r.member:
            recent_score = Score.query.filter_by(member_id=r.member_id).order_by(Score.training_date.desc()).first()
            if recent_score:
                bow_type = recent_score.bow_type
        result.append({
            'id': r.id,
            'exam_id': r.exam_id,
            'exam_name': r.exam.name if r.exam else '未知',
            'member_id': r.member_id,
            'member_name': r.member.name if r.member else '未知',
            'member_phone': r.member.phone if r.member else '',
            'member_level': r.member.tech_level if r.member else '',
            'bow_type': bow_type,
            'registration_time': r.registration_time,
            'status': r.status,
            'total_score': r.total_score,
            'ranking': r.ranking,
            'is_passed': r.is_passed,
            'level_upgraded': r.level_upgraded,
            'notes': r.notes
        })
    return jsonify(result)


@app.route('/api/exam-registrations/check-eligibility', methods=['POST'])
def check_registration_eligibility():
    data = request.json
    member_id = data['member_id']
    exam_id = data['exam_id']
    
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'eligible': False, 'reason': '会员不存在'})
    
    exam = LevelExam.query.get(exam_id)
    if not exam:
        return jsonify({'eligible': False, 'reason': '考试不存在'})
    
    if exam.status != '报名中':
        return jsonify({'eligible': False, 'reason': f'考试当前状态为"{exam.status}"，不接受报名'})
    
    today = date.today().isoformat()
    if today > exam.registration_deadline:
        return jsonify({'eligible': False, 'reason': '报名已截止'})
    
    registered_count = ExamRegistration.query.filter_by(exam_id=exam_id).count()
    if registered_count >= exam.registration_capacity:
        return jsonify({'eligible': False, 'reason': '报名人数已满'})
    
    existing = ExamRegistration.query.filter_by(exam_id=exam_id, member_id=member_id).first()
    if existing:
        return jsonify({'eligible': False, 'reason': '已报名该考试'})
    
    member_level, avg_score = calculate_tech_level(member_id)
    levels_order = ['白丁', '初级射手', '中级射手', '高级射手', '精英射手', '大师射手']
    target_idx = levels_order.index(exam.target_level)
    current_idx = levels_order.index(member_level)
    if current_idx >= target_idx:
        return jsonify({'eligible': False, 'reason': f'当前等级"{member_level}"已达到或超过目标等级"{exam.target_level}"'})
    if current_idx < target_idx - 1:
        return jsonify({'eligible': False, 'reason': f'需要先通过{levels_order[target_idx - 1]}等级考试'})
    
    recent_scores = Score.query.filter_by(member_id=member_id).order_by(Score.training_date.desc()).limit(5).all()
    if len(recent_scores) < 3:
        return jsonify({'eligible': False, 'reason': '近期训练成绩不足，需要至少3条训练记录'})
    
    recent_avg = sum(s.total_score for s in recent_scores) / len(recent_scores)
    if recent_avg < exam.pass_score * 0.6:
        return jsonify({'eligible': False, 'reason': f'近期训练平均成绩{recent_avg:.1f}过低，建议加强训练后再报名'})
    
    unreturned = BorrowRecord.query.filter_by(member_id=member_id, status='借用中').count()
    if unreturned > 0:
        return jsonify({'eligible': False, 'reason': f'存在{unreturned}件未归还器材，请先归还后再报名'})
    
    if exam.bow_type_restriction:
        allowed_bows = [b.strip() for b in exam.bow_type_restriction.split(',')]
        member_bow_scores = Score.query.filter_by(member_id=member_id).with_entities(Score.bow_type).distinct().all()
        member_bows = [b[0] for b in member_bow_scores]
        has_valid_bow = any(b in allowed_bows for b in member_bows)
        if not has_valid_bow and member_bows:
            return jsonify({'eligible': False, 'reason': f'考试限制弓型为{allowed_bows}，您的训练记录中未包含允许的弓型'})
    
    return jsonify({
        'eligible': True,
        'member_level': member_level,
        'avg_score': avg_score,
        'recent_avg': round(recent_avg, 2),
        'unreturned_count': unreturned
    })


@app.route('/api/exam-registrations', methods=['POST'])
def create_exam_registration():
    data = request.json
    member_id = data['member_id']
    exam_id = data['exam_id']
    
    eligibility = check_registration_eligibility()
    if not eligibility[0].is_json:
        return eligibility
    elig_result = eligibility[0].get_json()
    if not elig_result.get('eligible'):
        return jsonify({'message': elig_result.get('reason')}), 400
    
    registration = ExamRegistration(
        exam_id=exam_id,
        member_id=member_id,
        registration_time=data.get('registration_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        status='已报名',
        notes=data.get('notes', '')
    )
    db.session.add(registration)
    db.session.commit()
    return jsonify({'id': registration.id, 'message': '报名成功'})


@app.route('/api/exam-registrations/<int:id>', methods=['PUT'])
def update_exam_registration(id):
    registration = ExamRegistration.query.get(id)
    if not registration:
        return jsonify({'message': '报名记录不存在'}), 404
    data = request.json
    registration.status = data.get('status', registration.status)
    registration.notes = data.get('notes', registration.notes)
    db.session.commit()
    return jsonify({'message': '更新成功'})


@app.route('/api/exam-registrations/<int:id>', methods=['DELETE'])
def delete_exam_registration(id):
    registration = ExamRegistration.query.get(id)
    if not registration:
        return jsonify({'message': '报名记录不存在'}), 404
    ExamRoundScore.query.filter_by(registration_id=id).delete()
    ExamEquipmentReservation.query.filter_by(reserved_for_member_id=registration.member_id, exam_id=registration.exam_id).delete()
    db.session.delete(registration)
    db.session.commit()
    return jsonify({'message': '取消报名成功'})


@app.route('/api/exam-registrations/<int:id>/finalize', methods=['POST'])
def finalize_registration(id):
    registration = ExamRegistration.query.get(id)
    if not registration:
        return jsonify({'message': '报名记录不存在'}), 404
    
    exam = LevelExam.query.get(registration.exam_id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    
    round_scores = ExamRoundScore.query.filter_by(registration_id=id).all()
    total_score = sum(rs.round_total for rs in round_scores)
    registration.total_score = total_score
    
    all_registrations = ExamRegistration.query.filter_by(exam_id=exam.id).all()
    for reg in all_registrations:
        reg_scores = ExamRoundScore.query.filter_by(registration_id=reg.id).all()
        reg.total_score = sum(rs.round_total for rs in reg_scores)
    
    sorted_regs = sorted(all_registrations, key=lambda r: r.total_score, reverse=True)
    for i, reg in enumerate(sorted_regs):
        reg.ranking = i + 1
        reg.is_passed = reg.total_score >= exam.pass_score
    
    levels_order = ['白丁', '初级射手', '中级射手', '高级射手', '精英射手', '大师射手']
    target_idx = levels_order.index(exam.target_level)
    for reg in sorted_regs:
        if reg.is_passed:
            member = Member.query.get(reg.member_id)
            if member:
                current_level, _ = calculate_tech_level(reg.member_id)
                current_idx = levels_order.index(current_level)
                reg.level_upgraded = current_idx < target_idx
                if reg.level_upgraded:
                    member.tech_level = exam.target_level
    
    registration.status = '已完成'
    db.session.commit()
    
    return jsonify({
        'message': '成绩计算完成',
        'total_score': registration.total_score,
        'ranking': registration.ranking,
        'is_passed': registration.is_passed,
        'level_upgraded': registration.level_upgraded
    })


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


@app.route('/api/exam-round-scores', methods=['GET'])
def get_exam_round_scores():
    exam_id = request.args.get('exam_id', type=int)
    registration_id = request.args.get('registration_id', type=int)
    round_number = request.args.get('round_number', type=int)
    
    query = ExamRoundScore.query
    if exam_id:
        query = query.filter_by(exam_id=exam_id)
    if registration_id:
        query = query.filter_by(registration_id=registration_id)
    if round_number:
        query = query.filter_by(round_number=round_number)
    
    scores = query.order_by(ExamRoundScore.round_number, ExamRoundScore.id).all()
    return jsonify([{
        'id': s.id,
        'exam_id': s.exam_id,
        'registration_id': s.registration_id,
        'member_id': s.member_id,
        'member_name': s.registration.member.name if s.registration and s.registration.member else '未知',
        'round_number': s.round_number,
        'arrow_scores': s.arrow_scores,
        'arrow_scores_list': [int(x) for x in s.arrow_scores.split(',')] if s.arrow_scores else [],
        'round_total': s.round_total,
        'notes': s.notes,
        'recorded_by': s.recorded_by,
        'record_time': s.record_time
    } for s in scores])


@app.route('/api/exam-round-scores', methods=['POST'])
def create_exam_round_score():
    data = request.json
    registration = ExamRegistration.query.get(data['registration_id'])
    if not registration:
        return jsonify({'message': '报名记录不存在'}), 404
    
    exam = LevelExam.query.get(registration.exam_id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    
    arrow_scores = data.get('arrow_scores', [])
    if len(arrow_scores) != exam.arrows_per_round:
        return jsonify({'message': f'每轮箭数应为{exam.arrows_per_round}支'}), 400
    
    round_total = sum(arrow_scores)
    round_score = ExamRoundScore(
        exam_id=registration.exam_id,
        registration_id=data['registration_id'],
        member_id=registration.member_id,
        round_number=data['round_number'],
        arrow_scores=','.join(str(s) for s in arrow_scores),
        round_total=round_total,
        notes=data.get('notes', ''),
        recorded_by=data.get('recorded_by', '管理员'),
        record_time=data.get('record_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    )
    db.session.add(round_score)
    db.session.commit()
    return jsonify({'id': round_score.id, 'round_total': round_total, 'message': '成绩录入成功'})


@app.route('/api/exam-round-scores/<int:id>', methods=['PUT'])
def update_exam_round_score(id):
    round_score = ExamRoundScore.query.get(id)
    if not round_score:
        return jsonify({'message': '成绩记录不存在'}), 404
    data = request.json
    if 'arrow_scores' in data:
        arrow_scores = data['arrow_scores']
        round_score.arrow_scores = ','.join(str(s) for s in arrow_scores)
        round_score.round_total = sum(arrow_scores)
    if 'notes' in data:
        round_score.notes = data['notes']
    round_score.recorded_by = data.get('recorded_by', round_score.recorded_by)
    round_score.record_time = data.get('record_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    db.session.commit()
    return jsonify({'message': '成绩更新成功'})


@app.route('/api/exam-round-scores/<int:id>', methods=['DELETE'])
def delete_exam_round_score(id):
    round_score = ExamRoundScore.query.get(id)
    if not round_score:
        return jsonify({'message': '成绩记录不存在'}), 404
    db.session.delete(round_score)
    db.session.commit()
    return jsonify({'message': '成绩删除成功'})


@app.route('/api/exam-rankings/<int:exam_id>', methods=['GET'])
def get_exam_rankings(exam_id):
    exam = LevelExam.query.get(exam_id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    
    registrations = ExamRegistration.query.filter_by(exam_id=exam_id).all()
    for reg in registrations:
        if reg.status != '已完成':
            round_scores = ExamRoundScore.query.filter_by(registration_id=reg.id).all()
            reg.total_score = sum(rs.round_total for rs in round_scores)
    
    sorted_regs = sorted(registrations, key=lambda r: r.total_score, reverse=True)
    
    result = []
    for i, reg in enumerate(sorted_regs):
        member = Member.query.get(reg.member_id)
        round_scores = ExamRoundScore.query.filter_by(registration_id=reg.id).order_by(ExamRoundScore.round_number).all()
        round_totals = [rs.round_total for rs in round_scores]
        
        result.append({
            'ranking': i + 1,
            'registration_id': reg.id,
            'member_id': reg.member_id,
            'member_name': member.name if member else '未知',
            'member_level': member.tech_level if member else '',
            'total_score': reg.total_score,
            'round_totals': round_totals,
            'is_passed': reg.total_score >= exam.pass_score,
            'level_upgraded': reg.level_upgraded,
            'status': reg.status
        })
    
    return jsonify({
        'exam_name': exam.name,
        'pass_score': exam.pass_score,
        'total_rounds': exam.total_rounds,
        'rankings': result
    })


@app.route('/api/certificates/batch-issue', methods=['POST'])
def batch_issue_certificates():
    data = request.json
    exam_id = data['exam_id']
    registration_ids = data.get('registration_ids', [])
    
    exam = LevelExam.query.get(exam_id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    
    import uuid
    issued_certs = []
    
    query = ExamRegistration.query.filter_by(exam_id=exam_id, is_passed=True)
    if registration_ids:
        query = query.filter(ExamRegistration.id.in_(registration_ids))
    
    passed_registrations = query.all()
    
    for reg in passed_registrations:
        existing = Certificate.query.filter_by(exam_id=exam_id, member_id=reg.member_id).first()
        if existing:
            continue
        
        cert = Certificate(
            member_id=reg.member_id,
            exam_id=exam_id,
            level=exam.target_level,
            score=reg.total_score,
            issue_date=data.get('issue_date', date.today().isoformat()),
            certificate_number=f"ARCH-{date.today().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        )
        db.session.add(cert)
        issued_certs.append({
            'id': cert.id,
            'member_id': reg.member_id,
            'member_name': reg.member.name if reg.member else '未知',
            'certificate_number': cert.certificate_number,
            'level': cert.level,
            'score': cert.score
        })
    
    db.session.commit()
    return jsonify({'count': len(issued_certs), 'certificates': issued_certs, 'message': f'成功颁发{len(issued_certs)}张证书'})


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


@app.route('/api/exam-equipment-reservations', methods=['GET'])
def get_exam_equipment_reservations():
    exam_id = request.args.get('exam_id', type=int)
    member_id = request.args.get('member_id', type=int)
    
    query = ExamEquipmentReservation.query
    if exam_id:
        query = query.filter_by(exam_id=exam_id)
    if member_id:
        query = query.filter_by(reserved_for_member_id=member_id)
    
    reservations = query.order_by(ExamEquipmentReservation.reservation_time.desc()).all()
    return jsonify([{
        'id': r.id,
        'exam_id': r.exam_id,
        'exam_name': r.exam.name if r.exam else '未知',
        'equipment_id': r.equipment_id,
        'equipment_name': r.equipment.name if r.equipment else '未知',
        'equipment_type': r.equipment.type if r.equipment else '',
        'equipment_serial': r.equipment.serial_number if r.equipment else '',
        'equipment_status': r.equipment.status if r.equipment else '',
        'reserved_for_member_id': r.reserved_for_member_id,
        'reserved_for_member_name': r.reserved_for.name if r.reserved_for else '公共器材',
        'reservation_time': r.reservation_time,
        'start_time': r.start_time,
        'end_time': r.end_time,
        'status': r.status,
        'notes': r.notes
    } for r in reservations])


@app.route('/api/exam-equipment-reservations/available', methods=['GET'])
def get_available_equipment_for_exam():
    exam_id = request.args.get('exam_id', type=int)
    equipment_type = request.args.get('type', '')
    
    exam = LevelExam.query.get(exam_id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    
    reserved_ids = [r.equipment_id for r in ExamEquipmentReservation.query.filter_by(exam_id=exam_id).all()]
    
    query = Equipment.query.filter(Equipment.status == '可用', ~Equipment.id.in_(reserved_ids))
    if equipment_type:
        query = query.filter_by(type=equipment_type)
    
    equipments = query.all()
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'type': e.type,
        'serial_number': e.serial_number,
        'brand': e.brand,
        'status': e.status
    } for e in equipments])


@app.route('/api/exam-equipment-reservations/batch-reserve', methods=['POST'])
def batch_reserve_equipment():
    data = request.json
    exam_id = data['exam_id']
    equipment_ids = data['equipment_ids']
    start_time = data['start_time']
    end_time = data['end_time']
    member_id = data.get('member_id')
    
    exam = LevelExam.query.get(exam_id)
    if not exam:
        return jsonify({'message': '考试不存在'}), 404
    
    reserved_ids = [r.equipment_id for r in ExamEquipmentReservation.query.filter_by(exam_id=exam_id).all()]
    
    success_count = 0
    failed_count = 0
    reservations = []
    
    for eq_id in equipment_ids:
        if eq_id in reserved_ids:
            failed_count += 1
            continue
        
        equipment = Equipment.query.get(eq_id)
        if not equipment or equipment.status != '可用':
            failed_count += 1
            continue
        
        reservation = ExamEquipmentReservation(
            exam_id=exam_id,
            equipment_id=eq_id,
            reserved_for_member_id=member_id,
            reservation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            start_time=start_time,
            end_time=end_time,
            status='已预约',
            notes=data.get('notes', '')
        )
        db.session.add(reservation)
        success_count += 1
        reservations.append({
            'id': reservation.id,
            'equipment_id': eq_id,
            'equipment_name': equipment.name,
            'equipment_serial': equipment.serial_number
        })
    
    db.session.commit()
    return jsonify({
        'success_count': success_count,
        'failed_count': failed_count,
        'reservations': reservations,
        'message': f'成功预约{success_count}件器材，失败{failed_count}件'
    })


@app.route('/api/exam-equipment-reservations/<int:id>', methods=['PUT'])
def update_exam_equipment_reservation(id):
    reservation = ExamEquipmentReservation.query.get(id)
    if not reservation:
        return jsonify({'message': '预约记录不存在'}), 404
    data = request.json
    reservation.status = data.get('status', reservation.status)
    reservation.notes = data.get('notes', reservation.notes)
    if data.get('reserved_for_member_id'):
        reservation.reserved_for_member_id = data['reserved_for_member_id']
    db.session.commit()
    return jsonify({'message': '更新成功'})


@app.route('/api/exam-equipment-reservations/<int:id>', methods=['DELETE'])
def delete_exam_equipment_reservation(id):
    reservation = ExamEquipmentReservation.query.get(id)
    if not reservation:
        return jsonify({'message': '预约记录不存在'}), 404
    db.session.delete(reservation)
    db.session.commit()
    return jsonify({'message': '取消预约成功'})


@app.route('/api/statistics/exam-progress/<int:member_id>', methods=['GET'])
def get_member_exam_progress(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'message': '会员不存在'}), 404
    
    exam_registrations = ExamRegistration.query.filter_by(member_id=member_id, status='已完成').order_by(ExamRegistration.id).all()
    training_scores = Score.query.filter_by(member_id=member_id).order_by(Score.training_date).all()
    
    exam_progress = []
    for reg in exam_registrations:
        exam = LevelExam.query.get(reg.exam_id)
        if exam:
            exam_progress.append({
                'date': exam.exam_date,
                'type': 'exam',
                'score': reg.total_score,
                'exam_name': exam.name,
                'target_level': exam.target_level,
                'is_passed': reg.is_passed,
                'level_upgraded': reg.level_upgraded
            })
    
    training_progress = []
    for i, s in enumerate(training_scores):
        avg_score = sum(sc.total_score for sc in training_scores[:i+1]) / (i+1)
        training_progress.append({
            'date': s.training_date,
            'type': 'training',
            'score': s.total_score,
            'avg_score': round(avg_score, 2),
            'distance': s.target_distance,
            'bow_type': s.bow_type
        })
    
    all_progress = exam_progress + training_progress
    all_progress.sort(key=lambda x: x['date'])
    
    current_level, _ = calculate_tech_level(member_id)
    levels_order = ['白丁', '初级射手', '中级射手', '高级射手', '精英射手', '大师射手']
    
    return jsonify({
        'member_id': member_id,
        'member_name': member.name,
        'current_level': current_level,
        'current_level_index': levels_order.index(current_level),
        'total_exams': len(exam_registrations),
        'passed_exams': len([e for e in exam_registrations if e['is_passed']]),
        'exam_progress': exam_progress,
        'training_progress': training_progress,
        'all_progress': all_progress
    })


@app.route('/api/statistics/level-distribution-with-exams', methods=['GET'])
def get_level_distribution_with_exams():
    from sqlalchemy import func
    
    members = Member.query.all()
    distribution = {}
    for m in members:
        level, _ = calculate_tech_level(m.id)
        if level not in distribution:
            distribution[level] = {'count': 0, 'exam_count': 0, 'avg_score': 0}
        distribution[level]['count'] += 1
    
    exam_stats = ExamRegistration.query.filter_by(is_passed=True).with_entities(
        ExamRegistration.member_id,
        func.count(ExamRegistration.id).label('pass_count')
    ).group_by(ExamRegistration.member_id).all()
    
    for member_id, pass_count in exam_stats:
        member = Member.query.get(member_id)
        if member:
            level, avg = calculate_tech_level(member_id)
            if level in distribution:
                distribution[level]['exam_count'] += pass_count
                distribution[level]['avg_score'] = avg
    
    levels_order = ['白丁', '初级射手', '中级射手', '高级射手', '精英射手', '大师射手']
    result = []
    for level in levels_order:
        if level in distribution:
            d = distribution[level]
            result.append({
                'level': level,
                'count': d['count'],
                'exam_pass_count': d['exam_count'],
                'avg_score': round(d['avg_score'], 2) if d['count'] > 0 else 0
            })
    
    return jsonify(result)


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
