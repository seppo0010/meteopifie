"""
Create weather and forecast tables
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE weather (
            read_at TIMESTAMP,
            humidity FLOAT,
            temperature FLOAT,
            description VARCHAR(255)
        )
        """,
        "DROP TABLE weather"
    ),
    step(
        """
        CREATE TABLE forecast_date (
            read_at TIMESTAMP,
            date DATE,
            tempmin FLOAT,
            tempmax FLOAT,
            hummin FLOAT,
            hummax FLOAT
        )
        """,
        "DROP TABLE forecast_date"
    ),
    step(
        """
        CREATE TABLE forecast_timeofday (
            read_at TIMESTAMP,
            date DATE,
            tod VARCHAR(255),
            humidity FLOAT,
            temperature FLOAT,
            description VARCHAR(255)
        )
        """,
        "DROP TABLE forecast_timeofday"
    ),
]
