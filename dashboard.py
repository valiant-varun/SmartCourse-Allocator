import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import mysql.connector
from mysql.connector import Error

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
        df = pd.read_sql(query, conn)
        return df
    except Error as err:
        print(f"Error: '{err}'")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()

# --- Load and Prepare Data ---
students_df = get_data("SELECT * FROM Students;")
courses_df = get_data("SELECT * FROM Courses;")
preferences_df = get_data("SELECT * FROM Preferences;")
allocation_df = get_data("SELECT * FROM Allocation_Results;")
full_df = get_data("""
    SELECT 
        s.student_id, s.name, s.cgpa, s.major, 
        p.preference_rank, 
        ar.allocation_id IS NOT NULL AS allocated,
        c.course_name, c.max_capacity
    FROM Students s
    JOIN Preferences p ON s.student_id = p.student_id
    LEFT JOIN Allocation_Results ar ON p.student_id = ar.student_id AND p.course_id = ar.course_id
    LEFT JOIN Courses c ON p.course_id = c.course_id;
""")

if not students_df.empty and not courses_df.empty and not preferences_df.empty and not allocation_df.empty and not full_df.empty:

    # Prepare data for dashboard charts
    
    # Chart 1: Allocation Success Rate by Preference
    allocation_by_rank = pd.merge(allocation_df, preferences_df, on=['student_id', 'course_id'], how='inner')
    allocation_counts = allocation_by_rank['preference_rank'].value_counts().reset_index()
    allocation_counts.columns = ['Preference Rank', 'Students Allocated']

    # Chart 2: Demand vs Capacity
    demand_df = preferences_df.groupby('course_id').size().reset_index(name='total_preferences')
    demand_supply_df = pd.merge(demand_df, courses_df, on='course_id')
    demand_supply_df['Demand/Capacity Ratio'] = demand_supply_df['total_preferences'] / demand_supply_df['max_capacity']
    demand_supply_df.sort_values(by='Demand/Capacity Ratio', ascending=False, inplace=True)

    # NEW: Chart 3 - Allocation Success by Major
    success_by_major_df = full_df[full_df['preference_rank'] == 1].groupby('major')['allocated'].mean().reset_index()
    success_by_major_df['allocated'] = success_by_major_df['allocated'] * 100

    # NEW: Chart 4 - CGPA vs Allocation
    cgpa_allocation_df = full_df.drop_duplicates(subset=['student_id'])
    cgpa_allocation_df['allocated'] = cgpa_allocation_df['allocated'].astype(str).replace({'True': 'Allocated', 'False': 'Unallocated'})

    # NEW: Chart 5 - Courses with Remaining Seats
    vacancies_df = pd.merge(allocation_df, courses_df, on='course_id', how='right')
    vacancies_df = vacancies_df.groupby('course_id').agg(
        students_allocated=('student_id', 'count'),
        max_capacity=('max_capacity', 'first'),
        course_name=('course_name', 'first')
    ).reset_index()
    vacancies_df['remaining_seats'] = vacancies_df['max_capacity'] - vacancies_df['students_allocated']
    vacancies_df = vacancies_df[vacancies_df['remaining_seats'] > 0].sort_values(by='remaining_seats', ascending=False)


    # Calculate KPIs
    total_students = len(students_df)
    total_allocated = len(allocation_df['student_id'].unique())
    unallocated_count = total_students - total_allocated
    first_choice_success_rate = round(allocation_counts[allocation_counts['Preference Rank'] == 1]['Students Allocated'].sum() / total_allocated * 100, 2)
    unallocated_rate = round(unallocated_count / total_students * 100, 2)
    
    # --- Build the Dash App ---
    app = dash.Dash(__name__)

    app.layout = html.Div(children=[
        html.H1(children='Smart Course Allocator: Performance Dashboard', style={'textAlign': 'center'}),
        html.Hr(),
        
        # Section 1: Key Performance Indicators (KPIs)
        html.Div(children=[
            html.Div(children=[html.H3('Total Students'), html.P(f'{total_students}', style={'fontSize': 24})], className='kpi'),
            html.Div(children=[html.H3('Students Allocated'), html.P(f'{total_allocated}', style={'fontSize': 24})], className='kpi'),
            html.Div(children=[html.H3('Unallocated'), html.P(f'{unallocated_count}', style={'fontSize': 24})], className='kpi'),
            html.Div(children=[html.H3('1st Choice Success Rate'), html.P(f'{first_choice_success_rate}%', style={'fontSize': 24})], className='kpi'),
            html.Div(children=[html.H3('Unallocated Rate'), html.P(f'{unallocated_rate}%', style={'fontSize': 24})], className='kpi')
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
        html.Hr(),
        
        # Section 2: Main Charts
        html.Div(children=[
            dcc.Graph(
                id='allocation-success-chart',
                figure=px.pie(allocation_counts, values='Students Allocated', names='Preference Rank', title='Allocation Distribution by Preference Rank', hole=0.3)
            ),
            dcc.Graph(
                id='demand-capacity-chart',
                figure=px.bar(demand_supply_df.head(10), x='course_name', y='Demand/Capacity Ratio', title='Top 10 Courses by Demand/Capacity Ratio', labels={'course_name': 'Course Name', 'Demand/Capacity Ratio': 'Demand/Capacity Ratio'}, color='Demand/Capacity Ratio')
            )
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'}),
        html.Hr(),
        
        # Section 3: Additional Insights
        html.Div(children=[
            dcc.Graph(
                id='success-by-major-chart',
                figure=px.bar(success_by_major_df, x='major', y='allocated', title='1st Preference Success Rate by Major', labels={'allocated': 'Success Rate (%)', 'major': 'Major'}, color='allocated')
            ),
            dcc.Graph(
                id='cgpa-allocation-chart',
                figure=px.scatter(cgpa_allocation_df, x='cgpa', y='major', color='allocated', title='CGPA vs Allocation Status by Major', labels={'cgpa': 'CGPA', 'major': 'Major', 'allocated': 'Allocation Status'})
            )
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'}),

        # NEW: Chart 5 - Courses with Vacancies
        html.Div(children=[
            html.H3(children='Courses with Remaining Seats', style={'textAlign': 'center'}),
            dcc.Graph(
                id='vacant-courses-chart',
                figure=px.bar(vacancies_df, x='course_name', y='remaining_seats', title='Courses with Remaining Seats', labels={'course_name': 'Course Name', 'remaining_seats': 'Remaining Seats'})
            )
        ], style={'width': '80%', 'margin': 'auto', 'textAlign': 'center'})
    ])

    if __name__ == '__main__':
        app.run(debug=True)

else:
    print("Dashboard could not be launched due to data loading issues.")