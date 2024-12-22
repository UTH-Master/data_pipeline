
import psycopg2
from psycopg2 import sql
from config import DB_CONFIG

def line_intersection(line1, bbox):
    x1, y1, x2, y2 = bbox
    line_x1, line_y1, line_x2, line_y2 = line1

    denominator = ((line_x2 - line_x1) * (y2 - y1)) - ((line_y2 - line_y1) * (x2 - x1))
    if denominator == 0:
        return False

    t_numerator = ((x1 - line_x1) * (y2 - y1)) + ((line_y1 - y1) * (x2 - x1))
    u_numerator = ((x1 - line_x1) * (line_y2 - line_y1)) + ((line_y1 - y1) * (line_x2 - line_x1))

    t = t_numerator / denominator
    u = u_numerator / denominator
    if 0 <= t <= 1 and 0 <= u <= 1:
        return True

    return False


def insert_multiple_rows_from_dicts(table_name, data_list):
    """
    Insert multiple rows into a PostgreSQL table using a list of dictionaries.

    Parameters:
    table_name (str): Name of the table to insert data into.
    data_list (list): List of dictionaries containing column-value pairs.
    """
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        for data_dict in data_list:
            # Extract columns and values from the dictionary
            columns = ', '.join(data_dict.keys())
            placeholders = ', '.join(['%s'] * len(data_dict))
            values = tuple(data_dict.values())

            # Construct the SQL query dynamically
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

            # Execute the query
            cursor.execute(query, values)

        # Commit the changes
        connection.commit()
        print(f"Inserted {len(data_list)} rows successfully.")

    except psycopg2.Error as e:
        print(f"Error during multiple row insertion: {e}")

    finally:
        # Clean up and close the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()