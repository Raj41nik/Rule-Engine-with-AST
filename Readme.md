

---

# Rule Engine with AST 


This project is a web-based rule engine that allows users to:

- Create complex rules using a custom rule language.
- Visualize the Abstract Syntax Tree (AST) of the rules.
- Evaluate rules against user data.
- Modify existing rules.
- Store and retrieve rules from a database.

## Features

- **Rule Creation**: Input complex rules with logical operators (`AND`, `OR`, `NOT`), comparison operators (`>`, `<`, `=`, `>=`, `<=`), and parentheses.
- **AST Visualization**: Visualize the AST of the created rule using D3.js.
- **Rule Evaluation**: Evaluate the rule against user-provided data.
- **Rule Modification**: Modify existing rules by adding or removing conditions.
- **Rule Storage**: Store and retrieve rules from an SQLite database.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)


## Installation

### Prerequisites

- **Python 3.7+**
- **pip** package manager
- **Virtual Environment** (optional but recommended)
- **Git** (to clone the repository)

### Clone the Repository

```bash
git clone https://github.com/Raj41nik/task1.git
cd Rule-Engine-with-AST-Visualization
```

### Create a Virtual Environment (Optional)

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up the Database

The project uses SQLite as the database. The database file (`rules.db`) will be created automatically when you run the application.

### Run the Application

```bash
python app.py
```

The application will start at `http://127.0.0.1:5000/`.

## Usage

1. **Create a Rule**: Enter a rule in the **Create Rule** section and click **Create Rule**.
   - Example rule:
     ```
     age > 30 AND department = 'Sales'
     ```

2. **Visualize AST**: After creating the rule, the AST will be displayed on the right side.

3. **Evaluate Rule**: Enter user data in JSON format in the **Evaluate Rule** section and click **Evaluate Rule**.
   - Example user data:
     ```json
     {
       "age": 35,
       "department": "Sales"
     }
     ```

4. **Modify Rule**: Provide modification details in JSON format in the **Modify Rule** section and click **Modify Rule**.
   - Example modification:
     ```json
     {
       "action": "add_condition",
       "field": "experience",
       "operator": ">",
       "value": 5
     }
     ```

5. **Store Rule**: Click **Store Current Rule** to save the rule to the database.

## Project Structure

```
├── app.py              # Main application file
├── routes.py           # API routes and logic
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── static/
│   ├── particle/       # Backgroud Particle
│   ├── index.html      # Frontend HTML
│   ├── script.js       # Frontend JavaScript
│   ├── style.css       # Frontend CSS
│   └── images/
│       └── screenshot.png  # Screenshot of the application
└── templates/          # (Optional) HTML templates
```

## Dependencies

- **Flask**
- **Flask-RESTful**
- **Flask-SQLAlchemy**
- **lark-parser**

### Requirements.txt

Ensure your `requirements.txt` includes the following:

```
Flask
Flask-RESTful
Flask-SQLAlchemy
lark
```

You can generate it using:

```bash
pip freeze > requirements.txt
```

## Troubleshooting

- **Port Already in Use**: If port 5000 is in use, change the port in `app.py`:

  ```python
  app.run(debug=True, port=5001)
  ```

- **Module Not Found**: Ensure all dependencies are installed in your virtual environment.

- **Database Errors**: If you encounter database errors, delete the `rules.db` file and restart the application to recreate the database.


---

## Instructions for Running the Project on Any Machine

### Windows

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Raj41nik/task1.git
   Rule-Engine-with-AST-Visualization
   ```

2. **Create and Activate a Virtual Environment**:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python app.py
   ```

5. **Access the Application**:

   Open your web browser and navigate to `http://127.0.0.1:5000/`.

### macOS/Linux

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Raj41nik/task1.git
   cd Rule-Engine-with-AST-Visualization
   ```

2. **Create and Activate a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:

   ```bash
   python app.py
   ```

5. **Access the Application**:

   Open your web browser and navigate to `http://127.0.0.1:5000/`.

---
# AST
