from app import app
if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)