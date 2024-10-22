from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_string = db.Column(db.String, nullable=False)
    ast = db.Column(db.JSON, nullable=False)  # Store the serialized AST as JSON

    def __init__(self, rule_string, ast):
        self.rule_string = rule_string
        self.ast = ast
