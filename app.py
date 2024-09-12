import subprocess
import csv
from collections import defaultdict

# Specify the username to filter by
username = "paolo.concolato"

# Get commit dates from hg log for the specified user
log_output = subprocess.check_output(
    ["hg", "log", "-u", username, "--template", "{date|isodate}\n"], encoding="utf-8"
)

# Process the log output
commit_dates = log_output.splitlines()

# Count commits per day
commit_count = defaultdict(int)

for commit_date in commit_dates:
    # Extract only the date part (YYYY-MM-DD)
    date_str = commit_date.split(" ")[0]
    commit_count[date_str] += 1

# Write to CSV
with open("commit_heatmap.csv", "w", newline="") as csvfile:
    fieldnames = ["Date", "Commits"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for date, count in commit_count.items():
        writer.writerow({"Date": date, "Commits": count})

# Plot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Load the data
data = pd.read_csv("commit_heatmap.csv", parse_dates=["Date"])

# Ensure the 'Date' column is in datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Create a 'YearMonth' column for the heatmap (grouping by year and month)
data['YearMonth'] = data['Date'].dt.to_period('M')

# Create a pivot table with year and month for heatmap visualization
heatmap_data = data.groupby([data['YearMonth'], data['Date'].dt.weekday]).size().unstack(fill_value=0)

heatmap_data = heatmap_data.T

# Map weekday numbers to weekday names (first 3 letters)
weekday_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
heatmap_data.index = heatmap_data.index.map(weekday_names)

# Reindex to ensure all days of the week are included (even if they have no data)
full_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
heatmap_data = heatmap_data.reindex(full_week, fill_value=0)

# Get the current working directory
current_directory = Path.cwd()

# Extract the folder name
folder_name = current_directory.name

# Plot heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data, cmap="Blues", linewidths=0.5)
plt.title(f"Commit Heatmap for {folder_name} repository")
plt.ylabel("Day of Week")
plt.xlabel("Year-Month")
plt.show()
