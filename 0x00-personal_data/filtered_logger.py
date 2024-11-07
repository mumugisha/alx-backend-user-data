#!/usr/bin/env python3
"""
A function that defines hash password and returns hashed pwd.
"""

import logging
from typing import List
import re
import os
import mysql.connector
from mysql.connector import Error

PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """
    Returns the log message obfuscated.

    Args:
        fields (list): A list of strings representing all fields to obfuscate.
        redaction (str): A string representing by what the field will be
                         obfuscated.
        message (str): A string representing the log line.
        separator (str): A string representing the character separating all
                         fields in the log line.

    Returns:
        str: The redacted log message.
    """
    for field in fields:
        message = re.sub(f"{field}=.*?{separator}",
                         f"{field}={redaction}{separator}", message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class. """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Redacts sensitive information in the message instance of LogRecord.

        Args:
            record (LogRecord): LogRecord instance.

        Returns:
            str: The formatted and redacted string.
        """
        message = super(RedactingFormatter, self).format(record)
        return filter_datum(self.fields, self.REDACTION, message,
                            self.SEPARATOR)


def get_logger() -> logging.Logger:
    """
    Creates and configures a logger object.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = RedactingFormatter(PII_FIELDS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Connects to the database.

    Returns:
        mysql.connector.connection.MySQLConnection: MySQL database connection.
    """
    user = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    passwd = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    if not db_name:
        raise ValueError("The database name must be set in the environment.")

    try:
        connection = mysql.connector.connect(user=user, password=passwd,
                                             host=host, database=db_name)
        return connection
    except Error as err:
        logger = get_logger()
        logger.error(f"Error connecting to the database: {err}")
        raise


def main():
    """
    Main function that fetches data from the database and logs it.
    """
    logger = get_logger()
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users;")
        fields = cursor.column_names
        for row in cursor:
            message = "".join(f"{k}={v}; " for k, v in zip(fields, row))
            logger.info(message.strip())
    except Error as err:
        logger.error(f"Database error: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()


if __name__ == "__main__":
    main()
