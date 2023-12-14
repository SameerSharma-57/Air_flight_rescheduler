from datetime import datetime

def get_time_diff(d1, d2):
    formats = ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M']
    
    for format_str in formats:
        try:
            t1 = datetime.strptime(d1, format_str)
            t2 = datetime.strptime(d2, format_str)
            return (t2 - t1).total_seconds() / 3600
        except ValueError as e:
            print(f"Attempted format: {format_str}, Error: {e}")

    raise ValueError("No matching format found for the provided datetime strings")

# Example usage:
date_str1 = '2022-01-01 12:00:00'
date_str2 = '01/02/2022 14:30'

try:
    time_diff = get_time_diff(date_str1, date_str2)
    print(f"Time difference: {time_diff} hours")
except ValueError as e:
    print(f"Error: {e}")
