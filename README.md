# Smart Course Allocator: A Data-Driven Solution

This project presents a data-driven solution for optimizing course allocation in an academic setting. It goes beyond a simple allocation system by incorporating **advanced analytics** to provide actionable insights for academic resource planning and student satisfaction.

The system is designed to simulate a real-world problem where students compete for limited seats in high-demand courses. The core allocation logic prioritizes students based on their CGPA and course preferences, ensuring a fair and transparent process.

---

### 🚀 Key Features

* **Fair & Efficient Allocation:** Implements a sophisticated, multi-pass algorithm using SQL to allocate courses based on student CGPA and ranked preferences, while respecting course capacity limits.
* **Actionable Analytics:** Uses Python to analyze allocation results, identifying potential bottlenecks, demand patterns, and fairness issues across different student majors.
* **Professional Dashboard:** A dashboard built with Plotly Dash that visualizes key performance indicators (KPIs) like first-choice success rate, unallocated students, and a demand-to-capacity ratio for each course.
* **Consulting-Style Insights:** The project serves as a case study, providing data-backed recommendations to improve academic policy and resource management.

---

### 🛠️ Tech Stack

* **Database:** MySQL
* **Core Logic:** Python, SQL
* **Data Analysis:** Pandas, NumPy
* **Visualization:** Plotly, Dash
* **Version Control:** Git

---

### 📂 Repository Structure

The project is organized into clear, functional files:

* `create_database.py`: A Python script that creates the MySQL database, defines the table schemas, and populates them with realistic, synthetic data.
* `allocate_courses.py`: Contains the core Python and SQL logic to run the course allocation algorithm.
* `analytics.py`: A Python script for performing in-depth data analysis and generating static charts.
* `dashboard.py`: The script to launch the interactive, web-based dashboard using Plotly Dash.
* `course_allocator.db`: The SQLite database file (if used for local testing).
* `Figure_1.png`, `Figure_2.png`: Sample images of the generated charts and dashboards.

---

### 🏃 How to Run the Project Locally

Follow these steps to set up and run the project on your machine.

1.  **Prerequisites**
    * **Python 3.x:** Make sure Python is installed.
    * **MySQL Server:** Have a MySQL server running locally.
    * **MySQL Workbench:** Recommended for database management.

2.  **Environment Setup**
    * Clone the repository:
        ```bash
        git clone [https://github.com/valiant-varun/Smart_Course_Allocator.git](https://github.com/valiant-varun/Smart_Course_Allocator.git)
        cd Smart_Course_Allocator
        ```
    * Install the required Python libraries:
        ```bash
        pip install -r requirements.txt
        ```
        *Note: You may need to create a `requirements.txt` file by running `pip freeze > requirements.txt` after installing all project libraries.*

3.  **Database Setup**
    * Open MySQL Workbench and create a new schema (database) named `course_allocator_db`.
    * Update the MySQL credentials (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`) in both `create_database.py` and `allocate_courses.py` to match your local setup.
    * Run the database creation script to populate the tables with data:
        ```bash
        python create_database.py
        ```

4.  **Run the Allocation Algorithm**
    * Execute the main allocation script:
        ```bash
        python allocate_courses.py
        ```
    * This script will perform the allocation and print key metrics to your terminal.

5.  **View the Dashboard**
    * Launch the interactive dashboard:
        ```bash
        python dashboard.py
        ```
    * Open the provided URL (`http://127.0.0.1:8050/`) in your web browser to view the dashboard.

---

### 📈 Project Outcomes

This project successfully demonstrates the power of a data-driven approach to solving complex operational problems. The analysis reveals how student preferences, academic performance, and resource constraints interact, providing a clear roadmap for strategic decision-making in an academic environment.
