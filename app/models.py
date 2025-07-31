# models.py
from datetime import date, datetime, timezone
import uuid
from . import db

# --- B2B CLIENT (TENANT) MODEL ---
class Client(db.Model):
    __tablename__ = 'clients'
    __table_args__ = {'schema': 'neondb'}
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, unique=True)
    api_key = db.Column(db.String(128), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    users = db.relationship('User', back_populates='client')
    memberships = db.relationship('Membership', back_populates='client')
    diet_logs = db.relationship('DietLog', back_populates='client')
    workout_logs = db.relationship('WorkoutLog', back_populates='client')
    exercise_entries = db.relationship('ExerciseEntry', back_populates='client')
    weight_entries = db.relationship('WeightEntry', back_populates='client')
    measurement_logs = db.relationship('MeasurementLog', back_populates='client')
    workout_plans = db.relationship('WorkoutPlan', back_populates='client')
    achievements = db.relationship('Achievement', back_populates='client')
    # --- ADDED RELATIONSHIP FOR DIETPLAN ---
    diet_plans = db.relationship('DietPlan', back_populates='client')

    def __init__(self, company_name):
        self.company_name = company_name
        self.api_key = str(uuid.uuid4())

    def __repr__(self):
        return f'<Client {self.company_name}>'


# --- USER MODEL ---
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)

    username = db.Column(db.String(80), nullable=False)
    contact_info = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    fitness_goals = db.Column(db.Text)
    workouts_per_week = db.Column(db.String(10))
    workout_duration = db.Column(db.Integer)
    disliked_foods = db.Column(db.Text)
    allergies = db.Column(db.Text)
    health_conditions = db.Column(db.Text)
    sleep_hours = db.Column(db.String(10))
    stress_level = db.Column(db.String(20))
    activity_level = db.Column(db.String(50))

    client = db.relationship('Client', back_populates='users')
    membership = db.relationship('Membership', back_populates='user', uselist=False, cascade="all, delete-orphan")
    diet_logs = db.relationship('DietLog', back_populates='author', lazy=True, cascade="all, delete-orphan")
    workout_logs = db.relationship('WorkoutLog', back_populates='author', lazy=True, cascade="all, delete-orphan")
    weight_history = db.relationship('WeightEntry', back_populates='author', lazy=True, cascade="all, delete-orphan")
    measurement_logs = db.relationship('MeasurementLog', back_populates='author', lazy=True, cascade="all, delete-orphan")
    workout_plans = db.relationship('WorkoutPlan', back_populates='author', lazy=True, cascade="all, delete-orphan")
    achievements = db.relationship('Achievement', back_populates='author', lazy=True, cascade="all, delete-orphan")
    # --- ADDED RELATIONSHIP FOR DIETPLAN ---
    diet_plans = db.relationship('DietPlan', back_populates='author', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('username', 'client_id', name='_username_client_uc'),
        db.UniqueConstraint('contact_info', 'client_id', name='_contact_info_client_uc'),
        {'schema': 'neondb'}
    )


class Membership(db.Model):
    __tablename__ = 'membership'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    start_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date)
    plan = db.Column(db.String(50))

    client = db.relationship('Client', back_populates='memberships')
    user = db.relationship('User', back_populates='membership')

    __table_args__ = (
        {'schema': 'neondb'},
    )


class DietLog(db.Model):
    __tablename__ = 'diet_log'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    meal_name = db.Column(db.String(100), nullable=False)
    food_items = db.Column(db.Text)
    calories = db.Column(db.Integer)
    protein_g = db.Column(db.Float)
    carbs_g = db.Column(db.Float)
    fat_g = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = db.relationship('Client', back_populates='diet_logs')
    author = db.relationship('User', back_populates='diet_logs')
    
    __table_args__ = (
        {'schema': 'neondb'},
    )

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'meal_name': self.meal_name,
            'food_items': self.food_items, 'calories': self.calories,
            'protein_g': self.protein_g, 'carbs_g': self.carbs_g, 'fat_g': self.fat_g,
            'date': self.date.isoformat()
        }


# --- NEW DIETPLAN MODEL ---
class DietPlan(db.Model):
    __tablename__ = 'diet_plan'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    generated_plan = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = db.relationship('Client', back_populates='diet_plans')
    author = db.relationship('User', back_populates='diet_plans')

    __table_args__ = (
        {'schema': 'neondb'},
    )

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'generated_plan': self.generated_plan
        }


class WorkoutLog(db.Model):
    __tablename__ = 'workout_log'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = db.relationship('Client', back_populates='workout_logs')
    author = db.relationship('User', back_populates='workout_logs')
    exercises = db.relationship('ExerciseEntry', backref='workout_log', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        {'schema': 'neondb'},
    )

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'name': self.name,
            'date': self.date.isoformat(),
            'exercises': [exercise.to_dict() for exercise in self.exercises]
        }


class ExerciseEntry(db.Model):
    __tablename__ = 'exercise_entry'
    __table_args__ = {'schema': 'neondb'}
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    workout_log_id = db.Column(db.Integer, db.ForeignKey('neondb.workout_log.id'), nullable=False)

    client = db.relationship('Client', back_populates='exercise_entries')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'sets': self.sets,
            'reps': self.reps, 'weight': self.weight
        }


class WeightEntry(db.Model):
    __tablename__ = 'weight_entry'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = db.relationship('Client', back_populates='weight_entries')
    author = db.relationship('User', back_populates='weight_history')

    __table_args__ = (
        {'schema': 'neondb'},
    )

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id,
            'weight_kg': self.weight_kg, 'date': self.date.isoformat()
        }


class MeasurementLog(db.Model):
    __tablename__ = 'measurement_log'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    waist_cm = db.Column(db.Float)
    chest_cm = db.Column(db.Float)
    arms_cm = db.Column(db.Float)
    hips_cm = db.Column(db.Float)
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = db.relationship('Client', back_populates='measurement_logs')
    author = db.relationship('User', back_populates='measurement_logs')

    __table_args__ = (
        {'schema': 'neondb'},
    )

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'waist_cm': self.waist_cm,
            'chest_cm': self.chest_cm, 'arms_cm': self.arms_cm,
            'hips_cm': self.hips_cm, 'date': self.date.isoformat()
        }


class WorkoutPlan(db.Model):
    __tablename__ = 'workout_plan'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    generated_plan = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = db.relationship('Client', back_populates='workout_plans')
    author = db.relationship('User', back_populates='workout_plans')

    __table_args__ = (
        {'schema': 'neondb'},
    )

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'generated_plan': self.generated_plan
        }


class Achievement(db.Model):
    __tablename__ = 'achievement'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('neondb.clients.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('neondb.user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    unlocked_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    client = db.relationship('Client', back_populates='achievements')
    author = db.relationship('User', back_populates='achievements')

    __table_args__ = (
        {'schema': 'neondb'},
    )

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'name': self.name,
            'description': self.description, 'unlocked_at': self.unlocked_at.isoformat()
        }