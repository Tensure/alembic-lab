from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import logging

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Configure logging programmatically if not already configured
if not config.attributes.get("configure_logger", True):
    # Set up detailed logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure specific loggers for more verbose output
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)  # Show SQL statements
    logging.getLogger('alembic').setLevel(logging.INFO)
    logging.getLogger('alembic.runtime.migration').setLevel(logging.INFO)
    logging.getLogger('alembic.migration').setLevel(logging.INFO)
    logging.getLogger('root').setLevel(logging.INFO)
elif config.config_file_name is not None:
    # Fallback to file config if ini file exists
    fileConfig(config.config_file_name)

# No target metadata needed for day-2 operations - just apply migrations
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_database_url():
    """Get database URL from environment or config"""
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    logging.info(f"Using database URL: {url}")
    return url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    logging.info("Running migrations in OFFLINE mode")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        logging.info("Starting offline migration transaction")
        context.run_migrations()
        logging.info("Offline migration transaction completed")


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    logging.info("Running migrations in ONLINE mode")
    
    # Override the sqlalchemy.url with our environment variable
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    logging.info("Creating database engine...")
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        logging.info("Connected to database, starting migration context")
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            logging.info("Starting online migration transaction")
            context.run_migrations()
            logging.info("Online migration transaction completed")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
