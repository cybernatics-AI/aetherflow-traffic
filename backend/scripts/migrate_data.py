#!/usr/bin/env python3
"""
Data Migration Script for AetherFlow Backend
"""

import asyncio
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aetherflow.core.database import get_db_session
from aetherflow.core.logging import get_logger
from aetherflow.models.vehicle_data import VehicleData
from aetherflow.models.traffic_lights import TrafficLight
from aetherflow.models.user_accounts import UserAccount
from aetherflow.services.vehicle_service import VehicleDataService
from aetherflow.services.traffic_service import TrafficService

logger = get_logger(__name__)


class DataMigrator:
    """Handles data migration tasks"""
    
    def __init__(self):
        self.vehicle_service = VehicleDataService()
        self.traffic_service = TrafficService()
    
    async def import_vehicle_data_csv(self, csv_file: Path):
        """Import vehicle data from CSV file"""
        
        logger.info(f"Importing vehicle data from {csv_file}")
        
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file}")
        
        imported_count = 0
        error_count = 0
        
        async with get_db_session() as db:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Parse CSV row
                        vehicle_data = VehicleData(
                            vehicle_id=row['vehicle_id'],
                            speed=float(row['speed']),
                            latitude=float(row['latitude']),
                            longitude=float(row['longitude']),
                            heading=float(row.get('heading', 0)) if row.get('heading') else None,
                            altitude=float(row.get('altitude', 0)) if row.get('altitude') else None,
                            timestamp=datetime.fromisoformat(row['timestamp']),
                            device_type=row.get('device_type', 'unknown')
                        )
                        
                        # Generate data hash
                        vehicle_data.data_hash = self.vehicle_service._generate_data_hash(vehicle_data)
                        
                        db.add(vehicle_data)
                        imported_count += 1
                        
                        # Commit in batches
                        if imported_count % 1000 == 0:
                            await db.commit()
                            logger.info(f"Imported {imported_count} records...")
                    
                    except Exception as e:
                        logger.error(f"Error importing row {imported_count + error_count + 1}: {e}")
                        error_count += 1
                        continue
                
                # Final commit
                await db.commit()
        
        logger.info(f"Import completed: {imported_count} records imported, {error_count} errors")
        return imported_count, error_count
    
    async def import_traffic_lights_json(self, json_file: Path):
        """Import traffic lights from JSON file"""
        
        logger.info(f"Importing traffic lights from {json_file}")
        
        if not json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file}")
        
        with open(json_file, 'r') as f:
            traffic_lights_data = json.load(f)
        
        imported_count = 0
        error_count = 0
        
        async with get_db_session() as db:
            for light_data in traffic_lights_data:
                try:
                    traffic_light = TrafficLight(
                        intersection_id=light_data['intersection_id'],
                        latitude=float(light_data['latitude']),
                        longitude=float(light_data['longitude']),
                        light_phases=light_data.get('light_phases', ['red', 'yellow', 'green']),
                        current_phase=light_data.get('current_phase', 'red'),
                        timing_config=light_data.get('timing_config', {}),
                        status=light_data.get('status', 'active'),
                        installation_date=datetime.fromisoformat(light_data.get('installation_date', datetime.utcnow().isoformat()))
                    )
                    
                    db.add(traffic_light)
                    imported_count += 1
                
                except Exception as e:
                    logger.error(f"Error importing traffic light {light_data.get('intersection_id', 'unknown')}: {e}")
                    error_count += 1
                    continue
            
            await db.commit()
        
        logger.info(f"Import completed: {imported_count} traffic lights imported, {error_count} errors")
        return imported_count, error_count
    
    async def export_vehicle_data_csv(self, output_file: Path, days: int = 30):
        """Export vehicle data to CSV file"""
        
        logger.info(f"Exporting vehicle data to {output_file}")
        
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        async with get_db_session() as db:
            from sqlalchemy import select
            
            result = await db.execute(
                select(VehicleData)
                .where(VehicleData.timestamp >= cutoff_time)
                .order_by(VehicleData.timestamp)
            )
            vehicle_data = result.scalars().all()
        
        if not vehicle_data:
            logger.warning("No vehicle data found to export")
            return 0
        
        # Write to CSV
        with open(output_file, 'w', newline='') as f:
            fieldnames = [
                'id', 'vehicle_id', 'speed', 'latitude', 'longitude',
                'heading', 'altitude', 'timestamp', 'device_type',
                'is_validated', 'validation_score', 'reward_amount'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for vd in vehicle_data:
                writer.writerow({
                    'id': vd.id,
                    'vehicle_id': vd.vehicle_id,
                    'speed': vd.speed,
                    'latitude': vd.latitude,
                    'longitude': vd.longitude,
                    'heading': vd.heading,
                    'altitude': vd.altitude,
                    'timestamp': vd.timestamp.isoformat(),
                    'device_type': vd.device_type,
                    'is_validated': vd.is_validated,
                    'validation_score': vd.validation_score,
                    'reward_amount': float(vd.reward_amount or 0)
                })
        
        logger.info(f"Exported {len(vehicle_data)} vehicle data records")
        return len(vehicle_data)
    
    async def migrate_legacy_data(self, legacy_db_path: Path):
        """Migrate data from legacy database format"""
        
        logger.info(f"Migrating legacy data from {legacy_db_path}")
        
        # This is a placeholder for legacy data migration
        # Implementation would depend on the specific legacy format
        
        try:
            # Example: SQLite to SQLite migration
            import sqlite3
            
            legacy_conn = sqlite3.connect(legacy_db_path)
            legacy_conn.row_factory = sqlite3.Row
            
            # Migrate vehicle data
            cursor = legacy_conn.execute("SELECT * FROM legacy_vehicle_data")
            
            migrated_count = 0
            
            async with get_db_session() as db:
                for row in cursor:
                    try:
                        # Map legacy fields to new schema
                        vehicle_data = VehicleData(
                            vehicle_id=row['vehicle_id'],
                            speed=row['speed'],
                            latitude=row['lat'],  # Legacy field name
                            longitude=row['lon'],  # Legacy field name
                            timestamp=datetime.fromisoformat(row['created_at']),
                            device_type='legacy'
                        )
                        
                        # Generate missing fields
                        vehicle_data.data_hash = self.vehicle_service._generate_data_hash(vehicle_data)
                        
                        db.add(vehicle_data)
                        migrated_count += 1
                        
                        if migrated_count % 100 == 0:
                            await db.commit()
                            logger.info(f"Migrated {migrated_count} legacy records...")
                    
                    except Exception as e:
                        logger.error(f"Error migrating legacy record: {e}")
                        continue
                
                await db.commit()
            
            legacy_conn.close()
            
            logger.info(f"Legacy migration completed: {migrated_count} records migrated")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Legacy migration failed: {e}")
            raise
    
    async def cleanup_old_data(self, days: int = 90):
        """Clean up old data beyond retention period"""
        
        logger.info(f"Cleaning up data older than {days} days")
        
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        async with get_db_session() as db:
            from sqlalchemy import delete
            
            # Delete old vehicle data
            result = await db.execute(
                delete(VehicleData).where(VehicleData.timestamp < cutoff_time)
            )
            deleted_count = result.rowcount
            
            await db.commit()
        
        logger.info(f"Cleanup completed: {deleted_count} old records deleted")
        return deleted_count
    
    async def validate_data_integrity(self):
        """Validate data integrity across tables"""
        
        logger.info("Validating data integrity...")
        
        issues = []
        
        async with get_db_session() as db:
            from sqlalchemy import select, func
            
            # Check for duplicate vehicle IDs with same timestamp
            duplicate_result = await db.execute(
                select(VehicleData.vehicle_id, VehicleData.timestamp, func.count())
                .group_by(VehicleData.vehicle_id, VehicleData.timestamp)
                .having(func.count() > 1)
            )
            
            duplicates = duplicate_result.all()
            if duplicates:
                issues.append(f"Found {len(duplicates)} duplicate vehicle data entries")
            
            # Check for invalid coordinates
            invalid_coords_result = await db.execute(
                select(func.count())
                .where(
                    (VehicleData.latitude < -90) | (VehicleData.latitude > 90) |
                    (VehicleData.longitude < -180) | (VehicleData.longitude > 180)
                )
            )
            
            invalid_coords = invalid_coords_result.scalar()
            if invalid_coords > 0:
                issues.append(f"Found {invalid_coords} records with invalid coordinates")
            
            # Check for missing data hashes
            missing_hash_result = await db.execute(
                select(func.count())
                .where(VehicleData.data_hash.is_(None))
            )
            
            missing_hashes = missing_hash_result.scalar()
            if missing_hashes > 0:
                issues.append(f"Found {missing_hashes} records with missing data hashes")
        
        if issues:
            logger.warning("Data integrity issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✅ Data integrity validation passed")
        
        return issues
    
    async def generate_sample_data(self, count: int = 1000):
        """Generate sample data for testing"""
        
        logger.info(f"Generating {count} sample vehicle data records")
        
        import random
        from datetime import timedelta
        
        # NYC area bounds
        min_lat, max_lat = 40.4774, 40.9176
        min_lon, max_lon = -74.2591, -73.7004
        
        async with get_db_session() as db:
            for i in range(count):
                # Generate random vehicle data
                vehicle_data = VehicleData(
                    vehicle_id=f"SAMPLE_{i:06d}",
                    speed=random.uniform(0, 80),  # 0-80 km/h
                    latitude=random.uniform(min_lat, max_lat),
                    longitude=random.uniform(min_lon, max_lon),
                    heading=random.uniform(0, 360),
                    altitude=random.uniform(0, 100),
                    timestamp=datetime.utcnow() - timedelta(
                        minutes=random.randint(0, 60 * 24 * 7)  # Last week
                    ),
                    device_type=random.choice(['smartphone', 'gps_tracker', 'obd'])
                )
                
                # Generate data hash
                vehicle_data.data_hash = self.vehicle_service._generate_data_hash(vehicle_data)
                
                # Random validation
                vehicle_data.is_validated = random.choice([True, False])
                if vehicle_data.is_validated:
                    vehicle_data.validation_score = random.uniform(0.7, 1.0)
                    vehicle_data.reward_amount = random.uniform(0.001, 0.01)
                
                db.add(vehicle_data)
                
                if (i + 1) % 100 == 0:
                    await db.commit()
                    logger.info(f"Generated {i + 1} sample records...")
            
            await db.commit()
        
        logger.info(f"Sample data generation completed: {count} records created")
        return count


async def main():
    """Main migration function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="AetherFlow Data Migration Tool")
    subparsers = parser.add_subparsers(dest='command', help='Migration commands')
    
    # Import commands
    import_parser = subparsers.add_parser('import', help='Import data')
    import_parser.add_argument('--vehicle-csv', type=Path, help='Import vehicle data from CSV')
    import_parser.add_argument('--traffic-json', type=Path, help='Import traffic lights from JSON')
    import_parser.add_argument('--legacy-db', type=Path, help='Migrate from legacy database')
    
    # Export commands
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('--vehicle-csv', type=Path, help='Export vehicle data to CSV')
    export_parser.add_argument('--days', type=int, default=30, help='Number of days to export')
    
    # Maintenance commands
    maint_parser = subparsers.add_parser('maintenance', help='Data maintenance')
    maint_parser.add_argument('--cleanup', type=int, help='Clean up data older than N days')
    maint_parser.add_argument('--validate', action='store_true', help='Validate data integrity')
    maint_parser.add_argument('--generate-samples', type=int, help='Generate N sample records')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    migrator = DataMigrator()
    
    try:
        if args.command == 'import':
            if args.vehicle_csv:
                await migrator.import_vehicle_data_csv(args.vehicle_csv)
            elif args.traffic_json:
                await migrator.import_traffic_lights_json(args.traffic_json)
            elif args.legacy_db:
                await migrator.migrate_legacy_data(args.legacy_db)
            else:
                print("Please specify what to import")
        
        elif args.command == 'export':
            if args.vehicle_csv:
                await migrator.export_vehicle_data_csv(args.vehicle_csv, args.days)
            else:
                print("Please specify what to export")
        
        elif args.command == 'maintenance':
            if args.cleanup:
                await migrator.cleanup_old_data(args.cleanup)
            elif args.validate:
                await migrator.validate_data_integrity()
            elif args.generate_samples:
                await migrator.generate_sample_data(args.generate_samples)
            else:
                print("Please specify maintenance operation")
        
        logger.info("Migration operation completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
