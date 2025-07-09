"""
Simple migration runner for database day-2 operations
Just runs existing migrations - no creation, no complex features
"""
import os
import logging
from typing import Optional, Dict, Any
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class SimpleMigrationRunner:
    """Simple migration runner - just applies existing migrations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.alembic_cfg = self._create_config()
    
    def _create_config(self) -> Config:
        """Create minimal Alembic configuration"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        alembic_dir = os.path.join(project_root, "alembic")
        
        # Create config without ini file
        cfg = Config()
        cfg.set_main_option("script_location", alembic_dir)
        cfg.set_main_option("sqlalchemy.url", self.database_url)
        cfg.attributes["configure_logger"] = False
        
        return cfg
    
    def check_connection(self) -> Dict[str, Any]:
        """Check if database connection works"""
        try:
            logger.info(f"Testing database connection to: {self.database_url}")
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection successful")
            return {'success': True, 'message': 'Database connection successful'}
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_migrations(self, target_revision: str = "head") -> Dict[str, Any]:
        """Run migrations with detailed logging"""
        try:
            logger.info(f"Starting migration run to target: {target_revision}")
            
            # Get current revision before migration
            current_rev = self._get_current_revision()
            logger.info(f"Current database revision: {current_rev or 'None (empty database)'}")
            
            # Get the actual migration path that will be taken
            script = ScriptDirectory.from_config(self.alembic_cfg)
            
            # Determine the actual target revision (resolve "head" to actual revision)
            if target_revision == "head":
                head_rev = script.get_current_head()
                actual_target = head_rev
            else:
                actual_target = target_revision
            
            # Get the migration path from current to target
            migration_path = []
            try:
                if current_rev is None:
                    # Starting from scratch - get path from base to target
                    for rev in script.iterate_revisions(actual_target, None):
                        migration_path.append(rev.revision)
                    migration_path.reverse()  # We want chronological order
                else:
                    # Get path from current to target
                    for rev in script.iterate_revisions(actual_target, current_rev):
                        migration_path.append(rev.revision)
                    migration_path.reverse()  # We want chronological order
            except Exception as e:
                logger.warning(f"Could not determine migration path: {e}")
                migration_path = [actual_target] if actual_target != current_rev else []
            
            if not migration_path:
                logger.info("🎉 No pending migrations - database is up to date!")
                return {
                    'success': True, 
                    'message': 'No pending migrations - database is up to date',
                    'applied_migrations': [],
                    'final_revision': current_rev,
                    'target_revision': target_revision,
                    'previous_revision': current_rev
                }
            
            logger.info(f"🚀 Running alembic upgrade to '{target_revision}'...")
            logger.info(f"📋 Migration path: {' -> '.join([current_rev or 'None'] + migration_path)}")
            
            # Run the migration
            command.upgrade(self.alembic_cfg, target_revision)
            
            # Get final revision after migration
            final_rev = self._get_current_revision()
            logger.info(f"✅ Migration completed successfully! Final revision: {final_rev}")
            
            return {
                'success': True, 
                'message': f"Successfully migrated from {current_rev or 'None'} to {final_rev}",
                'applied_migrations': migration_path,
                'final_revision': final_rev,
                'target_revision': target_revision,
                'previous_revision': current_rev
            }
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_current_revision(self) -> Optional[str]:
        """Get the current database revision"""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                return context.get_current_revision()
        except Exception as e:
            logger.warning(f"Could not get current revision: {e}")
            return None


def apply_day2_operations(database_url: str, target_revision: str = "head") -> Dict[str, Any]:
    """Apply day-2 operations - main function for Lambda"""
    logger.info(f"Starting day-2 operations with target revision: {target_revision}")
    
    runner = SimpleMigrationRunner(database_url)
    
    # Check connection
    logger.info("Checking database connection...")
    conn_result = runner.check_connection()
    if not conn_result['success']:
        logger.error("Database connection failed, aborting migration")
        return conn_result
    
    # Run migrations
    logger.info("Database connection OK, proceeding with migrations...")
    result = runner.run_migrations(target_revision)
    
    if result['success']:
        logger.info("Day-2 operations completed successfully!")
    else:
        logger.error("Day-2 operations failed!")
    
    return result
