import mysql.connector
from mysql.connector import Error

# Replace with your MySQL details
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_DB = "course_allocator_db"

def create_db_connection():
    # ... (connection function remains the same)
    connection = None
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        print("MySQL Database connection successful.")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def run_query(connection, query, data=None):
    # ... (query execution function remains the same)
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
    except Error as err:
        print(f"Error: '{err}'")
        connection.rollback()
    finally:
        cursor.close()

def allocate_courses():
    connection = create_db_connection()
    if not connection:
        return

    print("\n--- Clearing previous allocation results ---")
    run_query(connection, "DELETE FROM Allocation_Results;")
    run_query(connection, "ALTER TABLE Allocation_Results AUTO_INCREMENT = 1;")

    # Loop through each preference rank (1, 2, 3)
    print("\n--- Starting allocation process ---")
    for rank in range(1, 4):
        print(f"\nAttempting to allocate courses for preference rank {rank}...")

        # Revised allocation query for a single run
        # This query is still a bit simple, but it's a good first fix.
        # It's better than the last version but still has limitations
        # on truly fair, granular allocation per course.
        allocation_query = f"""
            INSERT INTO Allocation_Results (student_id, course_id)
            SELECT
                t.student_id,
                t.course_id
            FROM (
                SELECT
                    p.student_id,
                    p.course_id,
                    ROW_NUMBER() OVER (PARTITION BY p.course_id ORDER BY s.cgpa DESC) as rn
                FROM
                    Preferences p
                JOIN
                    Students s ON p.student_id = s.student_id
                LEFT JOIN
                    Allocation_Results ar ON p.student_id = ar.student_id
                WHERE
                    p.preference_rank = {rank}
                    AND ar.student_id IS NULL
            ) as t
            JOIN
                Courses c ON t.course_id = c.course_id
            WHERE
                t.rn <= c.max_capacity
            ;
        """
        run_query(connection, allocation_query)
    
    # ... (rest of the code for reporting remains the same)
    print("\n--- Allocation process complete ---")
    print("\n--- Generating Allocation Metrics ---")
    get_allocation_metrics(connection)

    connection.close()

# The rest of the functions (get_allocation_metrics, and the __main__ block) remain the same.
# Make sure to include them from the previous response.

# ... (rest of the script remains the same)

def get_allocation_metrics(connection):
    """
    Calculates and prints key allocation metrics, including 3rd preference and unallocated students.
    """
    cursor = connection.cursor()

    # Metric 1: Total students allocated
    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM Allocation_Results;")
    allocated_count = cursor.fetchone()[0]
    print(f"Total students allocated: {allocated_count}")
    
    # Metric 2: Students who received their first choice
    cursor.execute("""
        SELECT COUNT(DISTINCT a.student_id)
        FROM Allocation_Results a
        JOIN Preferences p ON a.student_id = p.student_id AND a.course_id = p.course_id
        WHERE p.preference_rank = 1;
    """)
    first_choice_count = cursor.fetchone()[0]
    print(f"Students who received their first choice: {first_choice_count}")
    
    # Metric 3: Students who received their second choice
    cursor.execute("""
        SELECT COUNT(DISTINCT a.student_id)
        FROM Allocation_Results a
        JOIN Preferences p ON a.student_id = p.student_id AND a.course_id = p.course_id
        WHERE p.preference_rank = 2;
    """)
    second_choice_count = cursor.fetchone()[0]
    print(f"Students who received their second choice: {second_choice_count}")

    # NEW METRIC: Students who received their third choice
    cursor.execute("""
        SELECT COUNT(DISTINCT a.student_id)
        FROM Allocation_Results a
        JOIN Preferences p ON a.student_id = p.student_id AND a.course_id = p.course_id
        WHERE p.preference_rank = 3;
    """)
    third_choice_count = cursor.fetchone()[0]
    print(f"Students who received their third choice: {third_choice_count}")

    # NEW METRIC: Unallocated students
    cursor.execute("SELECT COUNT(*) FROM Students;")
    total_students = cursor.fetchone()[0]
    unallocated_count = total_students - allocated_count
    print(f"Total students: {total_students}")
    print(f"Total unallocated students: {unallocated_count}")

    # Metric 4: Courses with remaining seats (vacancies)
    cursor.execute("""
        SELECT c.course_name, c.max_capacity - COUNT(ar.student_id) AS remaining_seats
        FROM Courses c
        LEFT JOIN Allocation_Results ar ON c.course_id = ar.course_id
        GROUP BY c.course_id
        HAVING remaining_seats > 0
        ORDER BY remaining_seats DESC;
    """)
    vacant_courses = cursor.fetchall()
    print("\nCourses with Remaining Seats:")
    for course, seats in vacant_courses:
        print(f"- {course}: {seats} seats")
    
    # Metric 5: Courses that were oversubscribed
    cursor.execute("""
        SELECT c.course_name, COUNT(p.student_id) AS total_preferences, c.max_capacity
        FROM Courses c
        JOIN Preferences p ON c.course_id = p.course_id
        GROUP BY c.course_id
        HAVING total_preferences > c.max_capacity
        ORDER BY total_preferences DESC;
    """)
    oversubscribed_courses = cursor.fetchall()
    print("\nOversubscribed Courses (Demand > Capacity):")
    for course, demand, capacity in oversubscribed_courses:
        print(f"- {course}: Demand={demand}, Capacity={capacity}")

    cursor.close()

if __name__ == '__main__':
    allocate_courses()