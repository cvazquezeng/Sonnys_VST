from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ticket(db.Model):
    __tablename__ = 'ticket'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, unique=True, nullable=False)
    line_machine = db.Column(db.String(50), nullable=False)
    andon_status = db.Column(db.String(50), nullable=False)
    notification_groups = db.Column(db.String(1000), nullable=False)  # Increase size
    issue_type = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(1000), nullable=True)  # Increase size
    timestamp = db.Column(db.DateTime, nullable=False)
    color = db.Column(db.String(7), nullable=False)
    closed_at = db.Column(db.DateTime, nullable=True)  # Ensure this column is defined
    request_made_at = db.Column(db.DateTime, nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    notified = db.Column(db.Boolean, default=False)  # Add this line

    def __init__(self, ticket_id, line_machine, andon_status, notification_groups, issue_type, comment, timestamp, color, closed_at=None, request_made_at=None, acknowledged_at=None, notified=False):
        self.ticket_id = ticket_id
        self.line_machine = line_machine
        self.andon_status = andon_status
        self.notification_groups = notification_groups
        self.issue_type = issue_type
        self.comment = comment
        self.timestamp = timestamp
        self.color = color
        self.closed_at = closed_at
        self.request_made_at = request_made_at
        self.acknowledged_at = acknowledged_at
        self.notified = notified  # Add this line

    def time_elapsed(self):
        if self.andon_status.lower() == 'closed' and self.closed_at:
            return self.closed_at - self.timestamp
        return None

class ClosedTicket(db.Model):
    __tablename__ = 'closed_ticket'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, nullable=False, unique=True)
    line_machine = db.Column(db.String(100), nullable=False)
    request_made_at = db.Column(db.DateTime, nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    issue_type = db.Column(db.String(100), nullable=True)
    comment = db.Column(db.String(1000), nullable=True)  # Increase size
    notification_groups = db.Column(db.String(1000), nullable=True)  # Increase size

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'line_machine': self.line_machine,
            'issue_type': self.issue_type,
            'comment': self.comment,
            'request_made_at': self.request_made_at,
            'acknowledged_at': self.acknowledged_at,
            'closed_at': self.closed_at
        }
