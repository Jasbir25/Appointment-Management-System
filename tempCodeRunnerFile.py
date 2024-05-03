def modify_appointment_data(conn, appointment):
#     cur = conn.cursor()
#     cur.execute("""
#         UPDATE appointment
#         SET appointment_date =?, appointment_time =?, patient_name =?, reason =?
#         WHERE id =?
#     """, appointment)
#     conn.commit()
#     return True