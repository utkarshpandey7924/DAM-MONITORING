from flask import Flask, request, render_template_string
import pandas as pd

app = Flask(__name__)

# Load and clean the dataset
file_path = 'C:/Users/HP/Downloads/dam-monitorung/Book1.csv'
data = pd.read_csv(file_path, skiprows=2)

# Rename columns for clarity
data.columns = ['S.No.', 'Name of the Reservoir', 'District', 'Authorised Person', 'Contact No.',
                'LSL in Meter', 'FRL in Meter', 'Water Level', 'Today 8:00 AM', 'Rainfall in mm',
                'Unused 1', 'Unused 2', 'Unused 3', 'Unused 4', 'Unused 5', 'Unused 6', 'Unused 7']

# Data cleaning steps
data_cleaned = data.dropna(subset=['Name of the Reservoir'])
numeric_columns = ['LSL in Meter', 'FRL in Meter', 'Water Level', 'Today 8:00 AM', 'Rainfall in mm']
for col in numeric_columns:
    if col in data_cleaned.columns:
        data_cleaned[col] = pd.to_numeric(data_cleaned[col], errors='coerce')

def simple_threshold_based_prediction(data, max_dams=10):
    release_schedule = []
    threshold = 100

    # Sort the dams by water level in descending order
    sorted_data = data.sort_values(by='Water Level', ascending=False)
    
    # Select only the top `max_dams` dams
    top_dams = sorted_data.head(max_dams)

    # Define release times
    release_times = ["8:00 AM", "12:00 PM", "4:00 PM", "8:00 PM"]
    release_time_cycle = release_times * (max_dams // len(release_times) + 1)

    for index, row in top_dams.iterrows():
        dam = row.get('Name of the Reservoir', 'Unknown')
        water_level = row.get('Water Level', 0)
        
        release_time = release_time_cycle[index % len(release_times)]
        release_schedule.append((dam, release_time, water_level))
    
    return release_schedule

@app.route('/', methods=['GET', 'POST'])
def index():
    schedule = []
    num_dams = 0
    if request.method == 'POST':
        num_dams = int(request.form['num_dams'])
        if num_dams > 0:
            max_dams = min(num_dams, len(data_cleaned))
            schedule = simple_threshold_based_prediction(data_cleaned, max_dams=max_dams)
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dam Release Schedule</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121212;
            color: #FFFFFF;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
            transition: background-color 0.5s;
        }
        h1 {
            color: #FFFFFF;
            margin-bottom: 20px;
            font-size: 2.5rem;
            animation: fadeIn 1.5s ease-in-out;
        }
        .form-container {
            margin-bottom: 20px;
            text-align: center;
        }
        .form-container input[type="number"] {
            padding: 10px;
            font-size: 16px;
            border: 1px solid #333;
            border-radius: 5px;
            margin-right: 10px;
            color: #000;
            max-width: 200px;
        }
        .form-container input[type="submit"] {
            padding: 10px 20px;
            background-color: #1E90FF;
            color: #FFFFFF;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
            animation: fadeIn 2s ease-in-out;
        }
        .form-container input[type="submit"]:hover {
            background-color: #1C86EE;
        }
        .schedule-container {
            padding: 15px;
            border: 1px solid #333;
            background-color: #1C1C1C;
            max-width: 80%;
            border-radius: 10px;
            margin-top: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
            animation: slideUp 1.5s ease-out;
        }
        .schedule-item {
            padding: 10px;
            border-bottom: 1px solid #333;
            font-size: 18px;
            transition: transform 0.2s, background-color 0.3s;
        }
        .schedule-item.low {
            background-color: #32CD32; /* Green for low water level */
        }
        .schedule-item.medium {
            background-color: #FFA500; /* Amber for medium water level */
        }
        .schedule-item.high {
            background-color: #DC143C; /* Crimson for high water level */
        }
        .schedule-item:hover {
            transform: scale(1.05);
            background-color: #F08080; /* Light Coral for hover */
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @media (max-width: 600px) {
            h1 {
                font-size: 2rem;
            }
            .form-container input[type="number"], 
            .form-container input[type="submit"] {
                font-size: 14px;
            }
            .schedule-item {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <h1>Dam Release Schedule</h1>
    <div class="form-container">
        <form method="post" id="damForm">
            <input type="number" id="num_dams" name="num_dams" min="1" placeholder="Enter number of dams" required>
            <input type="submit" value="Get Schedule">
        </form>
    </div>

    {% if schedule %}
    <div class="schedule-container">
        <h2>Release Schedule</h2>
        {% for dam, time, level in schedule %}
        <div class="schedule-item {% if level <= 50 %}low{% elif level <= 100 %}medium{% else %}high{% endif %}">
            {{ dam }} should release water at {{ time }}.
        </div>
        {% endfor %}
        <p><strong>Total number of dams to release water: {{ schedule|length }}</strong></p>
    </div>
    {% endif %}
</body>
</html>
    ''', schedule=schedule)

if __name__ == '__main__':
    app.run(debug=True)

