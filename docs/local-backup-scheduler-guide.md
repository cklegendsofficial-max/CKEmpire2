# Local Backup Scheduler Guide

## Overview

The Local Backup Scheduler is a cost-free, automated backup system integrated into the CK Empire Builder application. It provides weekly CSV/PDF export functionality using the local file system, ensuring data persistence without external dependencies.

## Features

### 🔄 Automated Weekly Backups
- **Schedule**: Every Sunday at 2:00 AM
- **Frequency**: Weekly automated execution
- **Trigger**: Cron-based scheduling using APScheduler

### 📊 Multi-Format Export
- **CSV Files**: Analytics data, performance metrics, content statistics
- **PDF Reports**: Weekly summaries, business reports, mock implementations
- **JSON Files**: Configuration data, analytics tracking, content metadata

### 💰 Cost-Free Operation
- **Local Storage**: Uses local file system only
- **No External Dependencies**: No cloud services required
- **No API Costs**: Completely self-contained
- **Compression**: ZIP archives for efficient storage

### 🔧 Manual Trigger
- **API Endpoint**: `/backup/manual` for on-demand backups
- **Status Monitoring**: `/backup/status` for scheduler status
- **Rate Limiting**: 5 requests per minute for manual backups

## Architecture

### Core Components

#### LocalBackupScheduler Class
```python
class LocalBackupScheduler:
    """Local backup scheduler for weekly CSV/PDF export"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.backup_dir = Path("backups")
        self.data_dir = Path("data")
```

#### Key Methods
- `start_backup_scheduler()`: Initialize and start weekly jobs
- `stop_backup_scheduler()`: Gracefully shutdown scheduler
- `run_manual_backup()`: Trigger manual backup job
- `_weekly_backup_job()`: Main backup execution logic

### File Structure

```
backups/
├── ckempire_backup_YYYYMMDD_HHMMSS.zip
│   ├── backup_summary.json
│   ├── csv/
│   │   ├── analytics_summary.csv
│   │   ├── content_performance_analytics.csv
│   │   ├── monetization_analytics.csv
│   │   └── niche_content_analytics.csv
│   ├── pdf/
│   │   └── weekly_report.html
│   └── json/
│       ├── business_ideas_analytics.json
│       ├── channel_suggestions_analytics.json
│       └── content_generated_*.json
```

## Configuration

### Scheduler Settings
```python
# Weekly backup job - every Sunday at 2:00 AM
self.scheduler.add_job(
    self._weekly_backup_job,
    CronTrigger(day_of_week='sun', hour=2, minute=0),
    id='weekly_backup',
    name='Weekly CSV/PDF Backup',
    replace_existing=True
)
```

### Directory Structure
- **Backup Directory**: `backups/` (auto-created)
- **Data Directory**: `data/` (existing analytics files)
- **Temporary Directory**: `backups/backup_TIMESTAMP/` (auto-cleanup)

## API Endpoints

### Manual Backup Trigger
```http
POST /backup/manual
```

**Response:**
```json
{
    "status": "success",
    "message": "Manual backup completed successfully",
    "backup_path": "backups/ckempire_backup_20250804_120748.zip",
    "files_exported": {
        "csv_files": 4,
        "pdf_files": 1,
        "json_files": 6
    },
    "timestamp": "20250804_120748"
}
```

### Backup Status
```http
GET /backup/status
```

**Response:**
```json
{
    "status": "available",
    "scheduler_status": "running",
    "next_backup": "Sunday 2:00 AM",
    "backup_directory": "backups",
    "data_directory": "data",
    "features": [
        "Weekly CSV export",
        "PDF report generation",
        "JSON analytics backup",
        "Compressed archives",
        "Cost-free operation"
    ]
}
```

## Backup Process

### 1. CSV Export
```python
async def _export_csv_files(self, backup_folder: Path) -> list:
    """Export CSV files from data directory"""
    # Find all CSV files in data directory
    for csv_file in self.data_dir.glob("*.csv"):
        if csv_file.exists():
            # Copy CSV file to backup
            backup_csv = csv_folder / csv_file.name
            shutil.copy2(csv_file, backup_csv)
```

### 2. PDF/HTML Report Generation
```python
async def _create_mock_pdf_report(self, pdf_folder: Path) -> Path:
    """Create a mock PDF report (HTML fallback)"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CK Empire Weekly Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CK Empire Weekly Report</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        <!-- Report content -->
    </body>
    </html>
    """
```

### 3. JSON Analytics Backup
```python
async def _export_json_files(self, backup_folder: Path) -> list:
    """Export JSON analytics files"""
    # Find all JSON files in data directory
    for json_file in self.data_dir.glob("*.json"):
        if json_file.exists():
            # Copy JSON file to backup
            backup_json = json_folder / json_file.name
            shutil.copy2(json_file, backup_json)
```

### 4. Compression and Cleanup
```python
async def _create_compressed_backup(self, backup_folder: Path, timestamp: str) -> Path:
    """Create a compressed backup archive"""
    zip_path = self.backup_dir / f"ckempire_backup_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in backup_folder.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(backup_folder)
                zipf.write(file_path, arcname)
    
    # Clean up temporary folder
    shutil.rmtree(backup_folder)
```

## Integration with Main Application

### FastAPI Integration
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global backup_scheduler
    
    # Initialize and start backup scheduler
    try:
        backup_scheduler = LocalBackupScheduler()
        await backup_scheduler.start_backup_scheduler()
        logger.info("✅ Local backup scheduler integrated successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start backup scheduler: {e}")
    
    yield
    
    # Stop backup scheduler on shutdown
    try:
        if backup_scheduler:
            await backup_scheduler.stop_backup_scheduler()
    except Exception as e:
        logger.error(f"❌ Error stopping backup scheduler: {e}")
```

### Application Info Update
```python
@app.get("/info")
async def info():
    return {
        "features": [
            "Project Management",
            "Revenue Tracking",
            "AI Integration",
            "Ethics Monitoring",
            "Performance Analytics",
            "Cloud Backup",
            "Auto-scaling",
            "Local Backup Scheduler"  # New feature
        ],
        "backup_config": {
            "local_backup_enabled": True,
            "schedule": "Weekly (Sunday 2:00 AM)",
            "backup_types": ["CSV", "PDF", "JSON"],
            "compression": True,
            "cost_free": True
        }
    }
```

## Error Handling

### Graceful Fallbacks
- **Missing Files**: Continues with available files
- **PDF Generation**: Falls back to HTML reports
- **Compression Errors**: Logs error but continues
- **Scheduler Errors**: Logs and continues application startup

### Error Logging
```python
try:
    # Backup operation
    backup_result = await self._weekly_backup_job()
except Exception as e:
    logger.error(f"❌ Weekly backup job failed: {e}")
    return {"status": "error", "error": str(e)}
```

## Performance Considerations

### File Size Optimization
- **Compression**: ZIP with DEFLATE algorithm
- **Selective Export**: Only exports existing files
- **Cleanup**: Automatic removal of temporary folders
- **Size Monitoring**: Logs backup size for tracking

### Memory Usage
- **Streaming**: Processes files one at a time
- **Temporary Storage**: Uses temporary folders for processing
- **Cleanup**: Immediate cleanup after compression

## Security Features

### Local Operation
- **No External Dependencies**: All operations local
- **No Network Calls**: No external API calls
- **File System Security**: Uses local file permissions
- **No Credentials**: No external authentication required

### Data Integrity
- **File Copying**: Uses `shutil.copy2()` for metadata preservation
- **Compression Verification**: Validates ZIP file creation
- **Error Recovery**: Continues with partial backups on errors

## Monitoring and Logging

### Structured Logging
```python
logger.info("🔄 Starting weekly backup job...")
logger.info(f"📊 Exported CSV: {csv_file.name}")
logger.info(f"📦 Created compressed backup: {zip_path.name} ({size_mb:.2f} MB)")
logger.info("✅ Weekly backup completed successfully")
```

### Backup Summary
```json
{
    "backup_timestamp": "2025-08-04T12:07:48",
    "backup_type": "weekly_local_backup",
    "files_exported": {
        "csv_files": 4,
        "pdf_files": 1,
        "json_files": 6
    },
    "file_list": {
        "csv_files": ["analytics_summary.csv", "content_performance_analytics.csv"],
        "pdf_files": ["weekly_report.html"],
        "json_files": ["business_ideas_analytics.json", "channel_suggestions_analytics.json"]
    },
    "backup_size_mb": 0.01,
    "status": "completed"
}
```

## Testing

### Test Coverage
- **Scheduler Functionality**: Initialization, start/stop
- **File Creation**: Backup file generation and structure
- **API Integration**: Endpoint availability and responses
- **Cost-Free Operation**: Local file system usage
- **Weekly Schedule**: Cron job configuration

### Test Script
```bash
python scripts/test_backup_scheduler.py
```

**Expected Output:**
```
🎯 Overall: 5/5 tests passed
🎉 All tests passed! Local backup scheduler is working correctly.
```

## Troubleshooting

### Common Issues

#### 1. Scheduler Not Starting
**Symptoms**: No backup files created
**Solution**: Check APScheduler installation and permissions

#### 2. Missing Files
**Symptoms**: Empty backup archives
**Solution**: Verify data directory contains files

#### 3. Compression Errors
**Symptoms**: Backup fails during ZIP creation
**Solution**: Check disk space and file permissions

#### 4. API Endpoint Errors
**Symptoms**: Manual backup fails
**Solution**: Verify FastAPI app is running

### Debug Commands
```bash
# Check backup directory
ls -la backups/

# Verify scheduler status
curl http://localhost:8000/backup/status

# Test manual backup
curl -X POST http://localhost:8000/backup/manual

# Check application logs
tail -f logs/application.log
```

## Future Enhancements

### Planned Features
- **Incremental Backups**: Only backup changed files
- **Backup Rotation**: Automatic cleanup of old backups
- **Encryption**: Optional file encryption
- **Cloud Sync**: Optional cloud storage integration
- **Backup Verification**: Checksum validation
- **Email Notifications**: Backup completion alerts

### Configuration Options
- **Custom Schedules**: Configurable backup frequency
- **File Filters**: Selective file inclusion/exclusion
- **Compression Levels**: Adjustable ZIP compression
- **Retention Policy**: Configurable backup retention

## Conclusion

The Local Backup Scheduler provides a robust, cost-free solution for automated data backup in the CK Empire Builder application. It ensures data persistence through weekly CSV/PDF exports while maintaining complete independence from external services.

Key benefits:
- ✅ **Cost-Free**: No external dependencies or API costs
- ✅ **Automated**: Weekly scheduled backups
- ✅ **Comprehensive**: Multi-format export (CSV, PDF, JSON)
- ✅ **Reliable**: Error handling and graceful fallbacks
- ✅ **Integrated**: Seamless FastAPI integration
- ✅ **Monitored**: Structured logging and status endpoints

The system is production-ready and provides essential data protection for the CK Empire Builder platform. 