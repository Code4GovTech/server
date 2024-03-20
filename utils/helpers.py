from utils.connect_db import connect_db
import datetime
from utils.logging_file import logger

def calculate_points(percentage):
    if percentage >= 100:
        return 100
    elif percentage >= 75:
        return 75
    elif percentage >= 50:
        return 50
    else:
        return 0
    

def save_classroom_records(data):
    # Iterate over each object in the JSON array and insert into the database
    conn, cur = connect_db()    

    for record in data:
        try:
            cur.execute("""
                INSERT INTO public.github_classroom_data (assignment_id, assignment_name, assignment_url, c4gt_points, discord_id, github_username, points_available, points_awarded, roster_identifier, starter_code_url, student_repository_name, student_repository_url, submission_timestamp,updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                record['assignment_id'],
                record['assignment_name'],
                record['assignment_url'],
                record['c4gt_points'],
                record['discord_id'],
                record['github_username'],
                record['points_available'],
                record['points_awarded'],
                record['roster_identifier'],
                record['starter_code_url'],
                record['student_repository_name'],
                record['student_repository_url'],
                record['submission_timestamp'] if record['submission_timestamp'] else datetime.datetime.now(),
                record['updated_at']
            ))
            conn.commit()
            print("Record inserted successfully!")
        except Exception as e:
            conn.rollback()
            logger.info(e)
            print("Error inserting record:", e)

    # Close the cursor and connection
    cur.close()
    conn.close()

def update_classroom_records(data):
    # Iterate over each object in the JSON array and update the corresponding record in the database
    conn, cur = connect_db()    

    for record in data:
        try:
            cur.execute("""
                UPDATE public.github_classroom_data
                SET 
                    assignment_name = %s,
                    assignment_url = %s,
                    c4gt_points = %s,
                    github_username = %s,
                    points_available = %s,
                    points_awarded = %s,
                    roster_identifier = %s,
                    starter_code_url = %s,
                    student_repository_name = %s,
                    student_repository_url = %s,
                    submission_timestamp = %s,
                    updated_at = %s
                WHERE 
                    assignment_id = %s 
                    AND (discord_id IS NULL OR discord_id = %s);
            """, (
                record['assignment_name'],
                record['assignment_url'],
                record['c4gt_points'],
                record['github_username'],
                record['points_available'],
                record['points_awarded'],
                record['roster_identifier'],
                record['starter_code_url'],
                record['student_repository_name'],
                record['student_repository_url'],
                record['submission_timestamp'] if record['submission_timestamp'] else datetime.datetime.now(),
                record['updated_at'],
                str(record['assignment_id']),
                str(record['discord_id'])
            ))
            conn.commit()
            print("Record updated successfully!")
        except Exception as e:
            conn.rollback()
            logger.info(e)
            print("Error updating record:", e)

    # Close the cursor and connection
    cur.close()
    conn.close()