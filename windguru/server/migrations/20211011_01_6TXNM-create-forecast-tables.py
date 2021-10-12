"""
Create forecast tables
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE forecast_wg (
            read_at TIMESTAMP,
            forecast_date DATETIME,
            temperature FLOAT
        )
        """,
        "DROP TABLE forecast_wg"
    ),
]
