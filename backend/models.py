from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    join_date = db.Column(db.String(20), nullable=False)
    tech_level = db.Column(db.String(20), default='白丁')
    
    scores = db.relationship('Score', backref='member', lazy=True)
    borrow_records = db.relationship('BorrowRecord', backref='member', lazy=True)
    certificates = db.relationship('Certificate', backref='member', lazy=True)


class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    brand = db.Column(db.String(50), default='')
    status = db.Column(db.String(20), default='可用')
    buy_date = db.Column(db.String(20), nullable=False)
    
    borrow_records = db.relationship('BorrowRecord', backref='equipment', lazy=True)


class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    borrow_time = db.Column(db.String(20), nullable=False)
    expected_return = db.Column(db.String(20), nullable=False)
    actual_return = db.Column(db.String(20))
    status = db.Column(db.String(20), default='借用中')


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    target_distance = db.Column(db.Integer, nullable=False)
    bow_type = db.Column(db.String(30), nullable=False)
    arrows_count = db.Column(db.Integer, default=12)
    total_score = db.Column(db.Integer, nullable=False)
    training_date = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.String(200), default='')


class LevelExam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_level = db.Column(db.String(20), nullable=False)
    exam_date = db.Column(db.String(20), nullable=False)
    exam_location = db.Column(db.String(100), default='')
    pass_score = db.Column(db.Integer, default=100)
    status = db.Column(db.String(20), default='报名中')
    exam_project = db.Column(db.String(50), default='射箭')
    distance_group = db.Column(db.String(50), nullable=False)
    bow_type_restriction = db.Column(db.String(100), default='')
    registration_capacity = db.Column(db.Integer, default=50)
    registration_deadline = db.Column(db.String(20), nullable=False)
    arrows_per_round = db.Column(db.Integer, default=6)
    total_rounds = db.Column(db.Integer, default=12)
    
    registrations = db.relationship('ExamRegistration', backref='exam', lazy=True)
    round_scores = db.relationship('ExamRoundScore', backref='exam', lazy=True)
    equipment_reservations = db.relationship('ExamEquipmentReservation', backref='exam', lazy=True)
    certificates = db.relationship('Certificate', backref='exam', lazy=True)


class ExamRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('level_exam.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    registration_time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='已报名')
    total_score = db.Column(db.Integer, default=0)
    ranking = db.Column(db.Integer)
    is_passed = db.Column(db.Boolean, default=False)
    level_upgraded = db.Column(db.Boolean, default=False)
    notes = db.Column(db.String(200), default='')
    
    member = db.relationship('Member', backref='exam_registrations')
    round_scores = db.relationship('ExamRoundScore', backref='registration', lazy=True)


class ExamRoundScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('level_exam.id'), nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey('exam_registration.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    arrow_scores = db.Column(db.String(200), nullable=False)
    round_total = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(200), default='')
    recorded_by = db.Column(db.String(50), default='管理员')
    record_time = db.Column(db.String(20), nullable=False)


class ExamEquipmentReservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('level_exam.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    reserved_for_member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    reservation_time = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.String(20), nullable=False)
    end_time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='已预约')
    notes = db.Column(db.String(200), default='')
    
    equipment = db.relationship('Equipment', backref='exam_reservations')
    reserved_for = db.relationship('Member', backref='equipment_reservations')


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('level_exam.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    issue_date = db.Column(db.String(20), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
