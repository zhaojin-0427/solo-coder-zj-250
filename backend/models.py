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
    
    certificates = db.relationship('Certificate', backref='exam', lazy=True)


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('level_exam.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    issue_date = db.Column(db.String(20), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
