def create_hypertable(connection, table_name: str, time_column: str, chunk_time_interval: str = "1 day"):
    """Convert a regular table to a TimescaleDB hypertable"""
    connection.execute(
        f"SELECT create_hypertable('{table_name}', '{time_column}', chunk_time_interval => interval '{chunk_time_interval}')"
    )
