import mysql.connector
import pandas as pd
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns

# Replace with your MySQL details
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_DB = "course_allocator_db"

def get_data(query):
    """Connects to MySQL and returns data as a pandas DataFrame."""
    conn = None
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        print("Connection successful for data retrieval.")
        df = pd.read_sql(query, conn)
        return df
    except Error as err:
        print(f"Error: '{err}'")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def run_analytics():
    """Main function to run all analytics and generate reports."""
    
    # 1. Load all necessary data into DataFrames
    students_df = get_data("SELECT * FROM Students;")
    courses_df = get_data("SELECT * FROM Courses;")
    preferences_df = get_data("SELECT * FROM Preferences;")
    allocation_df = get_data("SELECT * FROM Allocation_Results;")
    
    if any(df is None for df in [students_df, courses_df, preferences_df, allocation_df]):
        print("Failed to load all data from the database. Please check your connection.")
        return

    print("\nData loaded successfully.")

    # 2. Key Metrics & Allocation Outcomes
    print("\n--- Key Allocation Metrics ---")
    total_students = len(students_df)
    total_allocated = len(allocation_df['student_id'].unique())
    first_choice_count = len(pd.merge(allocation_df, preferences_df[preferences_df['preference_rank'] == 1], on=['student_id', 'course_id']))
    second_choice_count = len(pd.merge(allocation_df, preferences_df[preferences_df['preference_rank'] == 2], on=['student_id', 'course_id']))
    third_choice_count = len(pd.merge(allocation_df, preferences_df[preferences_df['preference_rank'] == 3], on=['student_id', 'course_id']))
    
    print(f"Total Students: {total_students}")
    print(f"Total Allocated: {total_allocated}")
    print(f"Unallocated Students: {total_students - total_allocated}")
    print(f"Students with 1st Choice: {first_choice_count}")
    print(f"Students with 2nd Choice: {second_choice_count}")
    print(f"Students with 3rd Choice: {third_choice_count}")

    # --- 3. Demand vs. Capacity Analysis ---
    print("\n--- Demand vs. Capacity Analysis ---")
    
    # Calculate total preference count for each course
    demand_df = preferences_df.groupby('course_id').size().reset_index(name='total_preferences')
    
    # Merge with course capacity data
    demand_supply_df = pd.merge(demand_df, courses_df, on='course_id')
    demand_supply_df['demand_ratio'] = demand_supply_df['total_preferences'] / demand_supply_df['max_capacity']
    demand_supply_df.sort_values(by='demand_ratio', ascending=False, inplace=True)

    print("\nTop 5 Most Oversubscribed Courses (by Preference Ratio):")
    print(demand_supply_df[['course_name', 'total_preferences', 'max_capacity', 'demand_ratio']].head(5).to_string(index=False))
    
    # Visualization: Demand vs Capacity
    plt.figure(figsize=(12, 7))
    sns.barplot(x='course_name', y='demand_ratio', data=demand_supply_df.head(10))
    plt.title('Top 10 Courses by Demand-to-Capacity Ratio')
    plt.ylabel('Demand/Capacity Ratio')
    plt.xlabel('Course Name')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # --- 4. Fairness and CGPA Bias Analysis ---
    print("\n--- Fairness and CGPA Bias Analysis ---")
    
    # Merge all data for a comprehensive view
    full_df = pd.merge(preferences_df, students_df, on='student_id')
    full_df = pd.merge(full_df, allocation_df, on=['student_id', 'course_id'], how='left', suffixes=('_pref', '_alloc'))
    full_df['allocated'] = full_df['allocation_id'].notna()

    # Analyze allocation success by major
    success_by_major = full_df[full_df['preference_rank'] == 1].groupby('major')['allocated'].mean().reset_index()
    success_by_major['allocated'] = success_by_major['allocated'] * 100

    print("\n1st Preference Allocation Success Rate by Major:")
    print(success_by_major.to_string(index=False))

    # Visualization: 1st Preference Success Rate by Major
    plt.figure(figsize=(10, 6))
    sns.barplot(x='major', y='allocated', data=success_by_major)
    plt.title('1st Preference Allocation Success Rate by Major')
    plt.ylabel('Success Rate (%)')
    plt.xlabel('Major')
    plt.xticks(rotation=45)
    plt.show()

if __name__ == '__main__':
    run_analytics()