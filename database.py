import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="23ka1a0530@92",
        database="wholesale_management"
    )