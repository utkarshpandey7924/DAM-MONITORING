import pandas as pd

# Load the dataset, skipping initial rows and specifying the correct header row
file_path = 'C:/Users/HP/Downloads/dam-monitorung/Book1.csv'

# Read the file, skipping the first 2 rows and using the third row as header
data = pd.read_csv(file_path, skiprows=2)

# Print column names to check for discrepancies
print("Columns in the dataset:")
print(data.columns)

# Inspect the first few rows to understand the data
print("First few rows of the dataset:")
print(data.head())

# Rename columns for clarity if necessary
data.columns = ['S.No.', 'Name of the Reservoir', 'District', 'Authorised Person', 'Contact No.',
                'LSL in Meter', 'FRL in Meter', 'Water Level', 'Today 8:00 AM', 'Rainfall in mm',
                'Unused 1', 'Unused 2', 'Unused 3', 'Unused 4', 'Unused 5', 'Unused 6', 'Unused 7']

# Data cleaning steps
# Dropping rows where 'Name of the Reservoir' is NaN
data_cleaned = data.dropna(subset=['Name of the Reservoir'])

# Converting numeric columns to appropriate types
numeric_columns = ['LSL in Meter', 'FRL in Meter', 'Water Level', 'Today 8:00 AM', 'Rainfall in mm']
for col in numeric_columns:
    if col in data_cleaned.columns:
        data_cleaned[col] = pd.to_numeric(data_cleaned[col], errors='coerce')

def simple_threshold_based_prediction(data, max_dams=10):
    release_schedule = []
    threshold = 100  # Adjusted threshold to select more dams

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
        
        release_time = release_time_cycle[index % len(release_times)]  # Cycle through release times
        release_schedule.append(f'{dam} should release water at {release_time}.')
    
    return release_schedule

# Define a function to get a dynamic number of dams
def get_release_schedule(num_dams):
    if num_dams <= 0:
        print("Number of dams should be greater than 0.")
        return []
    # Ensure that the number of dams does not exceed the total available
    max_dams = min(num_dams, len(data_cleaned))
    schedule = simple_threshold_based_prediction(data_cleaned, max_dams=max_dams)
    return schedule

# Example usage
num_dams = 8  # Adjust this number as needed (5, 8, 12, etc.)
schedule = get_release_schedule(num_dams)

# Print the release schedule
for event in schedule:
    print(event)

# Print the total count of dams
print(f"\nTotal number of dams to release water: {len(schedule)}")
