from datetime import date, timedelta
from models import db, Member, Equipment, BorrowRecord, Score, LevelExam, Certificate, ExamRegistration, ExamRoundScore, ExamEquipmentReservation


def seed_data():
    if Member.query.count() > 0:
        return
    
    members = [
        Member(name='张三', phone='13800138001', join_date='2024-01-15', tech_level='中级射手'),
        Member(name='李四', phone='13800138002', join_date='2024-02-20', tech_level='初级射手'),
        Member(name='王五', phone='13800138003', join_date='2024-03-10', tech_level='高级射手'),
        Member(name='赵六', phone='13800138004', join_date='2024-04-05', tech_level='白丁'),
        Member(name='钱七', phone='13800138005', join_date='2024-05-12', tech_level='精英射手'),
    ]
    db.session.add_all(members)
    
    equipments = [
        Equipment(name='反曲弓', type='弓', serial_number='BOW-001', brand='HOYT', status='可用', buy_date='2023-06-01'),
        Equipment(name='反曲弓', type='弓', serial_number='BOW-002', brand='WIN&WIN', status='借用中', buy_date='2023-06-15'),
        Equipment(name='复合弓', type='弓', serial_number='BOW-003', brand='MATHEWS', status='可用', buy_date='2023-07-20'),
        Equipment(name='传统弓', type='弓', serial_number='BOW-004', brand='飞比克', status='可用', buy_date='2023-08-01'),
        Equipment(name='铝箭', type='箭', serial_number='ARR-001', brand='EASTON', status='可用', buy_date='2023-09-01'),
        Equipment(name='碳箭', type='箭', serial_number='ARR-002', brand='GOLD TIP', status='可用', buy_date='2023-09-15'),
        Equipment(name='护臂', type='护具', serial_number='GEAR-001', brand='NEET', status='可用', buy_date='2023-10-01'),
        Equipment(name='护胸', type='护具', serial_number='GEAR-002', brand='NEET', status='可用', buy_date='2023-10-10'),
        Equipment(name='护指', type='护具', serial_number='GEAR-003', brand='飞比克', status='借用中', buy_date='2023-10-20'),
    ]
    db.session.add_all(equipments)
    
    today = date.today()
    borrow_records = [
        BorrowRecord(member_id=1, equipment_id=2, borrow_time=(today - timedelta(days=1)).strftime('%Y-%m-%d 09:00:00'), expected_return=(today + timedelta(days=1)).strftime('%Y-%m-%d 18:00:00'), status='借用中'),
        BorrowRecord(member_id=3, equipment_id=9, borrow_time=(today - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'), expected_return=(today + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'), status='借用中'),
        BorrowRecord(member_id=2, equipment_id=1, borrow_time=(today - timedelta(days=5)).strftime('%Y-%m-%d 10:00:00'), expected_return=(today - timedelta(days=5)).strftime('%Y-%m-%d 18:00:00'), actual_return=(today - timedelta(days=5)).strftime('%Y-%m-%d 17:30:00'), status='已归还'),
        BorrowRecord(member_id=5, equipment_id=3, borrow_time=(today - timedelta(days=3)).strftime('%Y-%m-%d 08:00:00'), expected_return=(today - timedelta(days=3)).strftime('%Y-%m-%d 20:00:00'), actual_return=(today - timedelta(days=3)).strftime('%Y-%m-%d 19:45:00'), status='已归还'),
    ]
    db.session.add_all(borrow_records)
    
    scores_data = []
    for i, member_id in enumerate([1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 5, 5, 5, 5, 5]):
        days_ago = 30 - i * 2
        scores_data.append(Score(
            member_id=member_id,
            target_distance=[10, 18, 30, 50, 70][i % 5],
            bow_type=['反曲弓', '复合弓', '传统弓'][i % 3],
            arrows_count=12,
            total_score=60 + i * 5 + (member_id * 3),
            training_date=(today - timedelta(days=days_ago)).strftime('%Y-%m-%d'),
            notes=f'训练记录#{i+1}'
        ))
    db.session.add_all(scores_data)
    
    exams = [
        LevelExam(name='2024年春季等级考试-初级', target_level='初级射手', exam_date='2024-04-15', exam_location='主馆A区', pass_score=70, status='已完成',
                  exam_project='射箭', distance_group='18米', bow_type_restriction='反曲弓', registration_capacity=30,
                  registration_deadline='2024-04-10', arrows_per_round=6, total_rounds=12),
        LevelExam(name='2024年春季等级考试-中级', target_level='中级射手', exam_date='2024-04-15', exam_location='主馆B区', pass_score=90, status='已完成',
                  exam_project='射箭', distance_group='30米', bow_type_restriction='反曲弓,复合弓', registration_capacity=25,
                  registration_deadline='2024-04-10', arrows_per_round=6, total_rounds=12),
        LevelExam(name='2024年夏季等级考试-高级', target_level='高级射手', exam_date='2024-07-20', exam_location='户外靶场', pass_score=110, status='报名中',
                  exam_project='射箭', distance_group='50米', bow_type_restriction='反曲弓,复合弓,传统弓', registration_capacity=20,
                  registration_deadline='2024-07-15', arrows_per_round=6, total_rounds=12),
    ]
    db.session.add_all(exams)
    db.session.flush()
    
    registrations = [
        ExamRegistration(exam_id=1, member_id=2, registration_time='2024-04-05 10:30:00', status='已完成',
                         total_score=78, ranking=2, is_passed=True, level_upgraded=True),
        ExamRegistration(exam_id=1, member_id=4, registration_time='2024-04-06 14:20:00', status='已完成',
                         total_score=65, ranking=5, is_passed=False, level_upgraded=False),
        ExamRegistration(exam_id=2, member_id=1, registration_time='2024-04-05 11:00:00', status='已完成',
                         total_score=95, ranking=2, is_passed=True, level_upgraded=True),
        ExamRegistration(exam_id=2, member_id=5, registration_time='2024-04-06 09:30:00', status='已完成',
                         total_score=130, ranking=1, is_passed=True, level_upgraded=True),
        ExamRegistration(exam_id=3, member_id=1, registration_time='2024-06-10 15:00:00', status='已报名'),
        ExamRegistration(exam_id=3, member_id=3, registration_time='2024-06-12 10:30:00', status='已报名'),
    ]
    db.session.add_all(registrations)
    db.session.flush()
    
    round_scores_data = []
    for reg_id in [1, 2, 3, 4]:
        for round_num in range(1, 13):
            reg = ExamRegistration.query.get(reg_id)
            base_score = 60 if reg_id == 2 else 80
            arrow_scores = [str(max(0, min(10, base_score // 6 + i))) for i in range(6)]
            round_total = sum(int(s) for s in arrow_scores)
            round_scores_data.append(ExamRoundScore(
                exam_id=reg.exam_id,
                registration_id=reg_id,
                member_id=reg.member_id,
                round_number=round_num,
                arrow_scores=','.join(arrow_scores),
                round_total=round_total,
                notes=f'第{round_num}轮成绩',
                record_time=f'2024-04-15 10:{round_num * 5:02d}:00'
            ))
    db.session.add_all(round_scores_data)
    
    equipment_reservations = [
        ExamEquipmentReservation(exam_id=3, equipment_id=1, reserved_for_member_id=1,
                                 reservation_time='2024-06-15 10:00:00',
                                 start_time='2024-07-20 08:00:00', end_time='2024-07-20 12:00:00',
                                 status='已预约', notes='考试专用反曲弓'),
        ExamEquipmentReservation(exam_id=3, equipment_id=3, reserved_for_member_id=3,
                                 reservation_time='2024-06-15 10:30:00',
                                 start_time='2024-07-20 08:00:00', end_time='2024-07-20 12:00:00',
                                 status='已预约', notes='考试专用复合弓'),
        ExamEquipmentReservation(exam_id=3, equipment_id=5,
                                 reservation_time='2024-06-15 11:00:00',
                                 start_time='2024-07-20 08:00:00', end_time='2024-07-20 18:00:00',
                                 status='已预约', notes='考试备用铝箭'),
    ]
    db.session.add_all(equipment_reservations)
    
    certificates = [
        Certificate(member_id=1, exam_id=2, level='中级射手', score=95, issue_date='2024-04-16', certificate_number='ARCH-20240416-A1B2C3D4'),
        Certificate(member_id=2, exam_id=1, level='初级射手', score=78, issue_date='2024-04-16', certificate_number='ARCH-20240416-E5F6G7H8'),
        Certificate(member_id=5, exam_id=2, level='中级射手', score=130, issue_date='2024-04-16', certificate_number='ARCH-20240416-I9J0K1L2'),
    ]
    db.session.add_all(certificates)
    
    db.session.commit()
