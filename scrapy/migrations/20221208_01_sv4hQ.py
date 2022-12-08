"""

"""

from yoyo import step

__depends__ = {'20211008_01_odw7a-create-weather-and-forecast-tables'}

steps = [
    step("""
    ALTER TABLE forecast_timeofday ADD COLUMN rainprobmin FLOAT;
    ALTER TABLE forecast_timeofday ADD COLUMN rainprobmax FLOAT;
    """)
]
