import mysql.connector
from mysql.connector import Error
import random

# Replace with your MySQL details
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_DB = "course_allocator_db"

def create_db_connection():
    """
    Creates a database connection to the MySQL Server
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def create_tables(connection):
    """
    Sets up the necessary tables in the MySQL database.
    """
    cursor = connection.cursor()

    # Drop tables in a specific order to avoid foreign key constraints
    print("Dropping existing tables...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("DROP TABLE IF EXISTS Allocation_Results;")
    cursor.execute("DROP TABLE IF EXISTS Preferences;")
    cursor.execute("DROP TABLE IF EXISTS Students;")
    cursor.execute("DROP TABLE IF EXISTS Courses;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # Create Students table
    cursor.execute('''
        CREATE TABLE Students (
            student_id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            cgpa DECIMAL(3, 2) NOT NULL,
            major VARCHAR(255)
        );
    ''')

    # Create Courses table
    cursor.execute('''
        CREATE TABLE Courses (
            course_id INT PRIMARY KEY,
            course_name VARCHAR(255) NOT NULL,
            department VARCHAR(255) NOT NULL,
            max_capacity INT NOT NULL
        );
    ''')

    # Create Preferences table
    cursor.execute('''
        CREATE TABLE Preferences (
            pref_id INT PRIMARY KEY AUTO_INCREMENT,
            student_id INT,
            course_id INT,
            preference_rank INT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        );
    ''')

    # Create Allocation_Results table (initially empty)
    cursor.execute('''
        CREATE TABLE Allocation_Results (
            allocation_id INT PRIMARY KEY AUTO_INCREMENT,
            student_id INT,
            course_id INT,
            FOREIGN KEY (student_id) REFERENCES Students(student_id),
            FOREIGN KEY (course_id) REFERENCES Courses(course_id)
        );
    ''')
    connection.commit()
    print("Tables created successfully.")

# ... (all imports and functions before populate_sample_data remain the same)

def populate_sample_data(connection):
    """
    Populates the database with sample students, courses, and preferences.
    This version creates imbalanced data with popular courses.
    """
    cursor = connection.cursor()

    # Clear existing data before re-populating
    print("Clearing existing data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE Students;")
    cursor.execute("TRUNCATE TABLE Courses;")
    cursor.execute("TRUNCATE TABLE Preferences;")
    cursor.execute("TRUNCATE TABLE Allocation_Results;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    connection.commit()

    # --- 1. Realistic Students Data ---
    student_data = []
    majors = ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Business', 'Arts & Humanities']
    
    # Create the initial 200 students
    for i in range(1, 201):  # 200 students
        student_data.append((i, f'Student_{i}', round(random.uniform(2.5, 4.0), 2), random.choice(majors)))
    
    # Introduce some "star" students with high CGPA, using new IDs
    student_data.extend([(201, 'Star_Student_A', 3.99, 'Computer Science'),
                         (202, 'Star_Student_B', 3.98, 'Computer Science')])
    
    print("Populating Students table...")
    cursor.executemany("INSERT INTO Students (student_id, name, cgpa, major) VALUES (%s, %s, %s, %s);", student_data)

    # --- 2. Courses with Varied Capacity ---
    course_data = [
        # Highly popular courses with limited seats (Demand > Capacity)
        (101, 'Data Structures', 'CS', 10),
        (102, 'Algorithms', 'CS', 10),
        (103, 'Machine Learning', 'CS', 8),
        (104, 'Intro to AI', 'CS', 8),
        (105, 'Quantum Computing', 'CS', 5), # Very competitive
        
        # Moderately popular courses (Demand ≈ Capacity)
        (106, 'Digital Logic Design', 'EE', 25),
        (107, 'Thermodynamics', 'ME', 20),
        (108, 'Financial Accounting', 'Business', 35),
        
        # Low demand courses (Capacity > Demand)
        (109, 'World History', 'Arts', 30),
        (110, 'Creative Writing', 'Arts', 25)
    ]
    print("Populating Courses table...")
    cursor.executemany("INSERT INTO Courses (course_id, course_name, department, max_capacity) VALUES (%s, %s, %s, %s);", course_data)

    # --- 3. Realistic Preferences Data ---
    preference_data = []
    hot_courses = [101, 102, 103, 104, 105] 
    
    # 80% of students will put a hot course as their first preference
    for student_id in range(1, 161): # 160 students
        pref_1 = random.choice(hot_courses)
        remaining_courses = [c[0] for c in course_data if c[0] != pref_1]
        prefs = random.sample(remaining_courses, 2)
        preference_data.append((student_id, pref_1, 1))
        preference_data.append((student_id, prefs[0], 2))
        preference_data.append((student_id, prefs[1], 3))

    # The other 20% of students plus the star students have more varied preferences
    for student_id in range(161, 203): # Including the two star students (ID 201, 202)
        all_courses = [c[0] for c in course_data]
        prefs = random.sample(all_courses, 3)
        preference_data.append((student_id, prefs[0], 1))
        preference_data.append((student_id, prefs[1], 2))
        preference_data.append((student_id, prefs[2], 3))

    print("Populating Preferences table...")
    cursor.executemany("INSERT INTO Preferences (student_id, course_id, preference_rank) VALUES (%s, %s, %s);", preference_data)
    
    connection.commit()
    print("Sample data populated successfully.")
    cursor.close()

# ... (main block remains the same)

if __name__ == '__main__':
    # Ensure the database exists in MySQL Workbench before running this script
    connection = create_db_connection()
    if connection:
        create_tables(connection)
        populate_sample_data(connection)
        connection.close()