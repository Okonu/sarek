#!/usr/bin/env python3
"""
System monitoring for Sarek AI Assistant
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

try:
    import psutil

    SYSTEM_MONITORING = True
except ImportError:
    SYSTEM_MONITORING = False

from ..constants import DB_PATH


class SystemMonitor:
    """System performance monitoring and health assessment"""

    def __init__(self):
        self.available = SYSTEM_MONITORING

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        if not self.available:
            return {'error': 'System monitoring not available (install psutil)'}

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()

            memory = psutil.virtual_memory()

            disk = psutil.disk_usage('/')

            process_count = len(psutil.pids())

            boot_time = datetime.fromtimestamp(psutil.boot_time())

            return {
                'cpu': {
                    'usage_percent': round(cpu_percent, 1),
                    'cores_logical': psutil.cpu_count(logical=True),
                    'cores_physical': psutil.cpu_count(logical=False),
                    'frequency_mhz': round(cpu_freq.current, 1) if cpu_freq else 0
                },
                'memory': {
                    'total_gb': round(memory.total / (1024 ** 3), 2),
                    'used_gb': round(memory.used / (1024 ** 3), 2),
                    'usage_percent': round(memory.percent, 1),
                    'available_gb': round(memory.available / (1024 ** 3), 2)
                },
                'disk': {
                    'total_gb': round(disk.total / (1024 ** 3), 2),
                    'used_gb': round(disk.used / (1024 ** 3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 1),
                    'free_gb': round(disk.free / (1024 ** 3), 2)
                },
                'system': {
                    'processes': process_count,
                    'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'uptime_hours': round((datetime.now() - boot_time).total_seconds() / 3600, 1)
                }
            }
        except Exception as e:
            return {'error': f'System monitoring error: {e}'}

    def get_health_assessment(self) -> Dict[str, Any]:
        """Assess system health and provide recommendations"""
        metrics = self.get_system_metrics()

        if 'error' in metrics:
            return metrics

        assessment = {
            'overall_health': 'good',
            'warnings': [],
            'critical_issues': [],
            'recommendations': [],
            'score': 100
        }

        cpu_usage = metrics['cpu']['usage_percent']
        if cpu_usage > 90:
            assessment['critical_issues'].append("Critical CPU usage (>90%)")
            assessment['recommendations'].append("Check for resource-intensive processes")
            assessment['overall_health'] = 'critical'
            assessment['score'] -= 30
        elif cpu_usage > 70:
            assessment['warnings'].append("High CPU usage (>70%)")
            assessment['recommendations'].append("Monitor CPU-heavy applications")
            if assessment['overall_health'] == 'good':
                assessment['overall_health'] = 'warning'
            assessment['score'] -= 15

        memory_usage = metrics['memory']['usage_percent']
        if memory_usage > 90:
            assessment['critical_issues'].append("Critical memory usage (>90%)")
            assessment['recommendations'].append("Close unnecessary applications or add more RAM")
            assessment['overall_health'] = 'critical'
            assessment['score'] -= 25
        elif memory_usage > 80:
            assessment['warnings'].append("High memory usage (>80%)")
            assessment['recommendations'].append("Consider closing some applications")
            if assessment['overall_health'] == 'good':
                assessment['overall_health'] = 'warning'
            assessment['score'] -= 10

        disk_usage = metrics['disk']['usage_percent']
        if disk_usage > 95:
            assessment['critical_issues'].append("Disk space critically low (<5% free)")
            assessment['recommendations'].append("Free up disk space immediately")
            assessment['overall_health'] = 'critical'
            assessment['score'] -= 25
        elif disk_usage > 85:
            assessment['warnings'].append("Low disk space (<15% free)")
            assessment['recommendations'].append("Clean up unnecessary files")
            if assessment['overall_health'] == 'good':
                assessment['overall_health'] = 'warning'
            assessment['score'] -= 10

        uptime = metrics['system']['uptime_hours']
        if uptime > 720:
            assessment['warnings'].append("System has been running for >30 days")
            assessment['recommendations'].append("Consider restarting to apply updates")
            assessment['score'] -= 5

        return assessment

    def get_process_info(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get information about running processes"""
        if not self.available:
            return []

        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': round(pinfo['cpu_percent'], 1),
                        'memory_percent': round(pinfo['memory_percent'], 1)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]

        except Exception:
            return []

    def get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        if not self.available:
            return {'error': 'System monitoring not available'}

        try:
            net_io = psutil.net_io_counters()

            interfaces = psutil.net_if_addrs()

            return {
                'io_stats': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'interfaces': {
                    name: [
                        {
                            'family': addr.family.name,
                            'address': addr.address,
                            'netmask': addr.netmask
                        }
                        for addr in addrs
                    ]
                    for name, addrs in interfaces.items()
                }
            }
        except Exception as e:
            return {'error': f'Network info error: {e}'}

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics from database and system"""
        stats = {}

        try:
            with sqlite3.connect(DB_PATH) as conn:

                cursor = conn.execute("SELECT COUNT(*) FROM conversations")
                stats['conversations'] = cursor.fetchone()[0]

                cursor = conn.execute("SELECT COUNT(*) FROM sessions")
                stats['sessions'] = cursor.fetchone()[0]

                cursor = conn.execute("SELECT COUNT(*) FROM code_analysis")
                stats['code_analyses'] = cursor.fetchone()[0]

                db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
                stats['database_size_mb'] = round(db_size / (1024 * 1024), 2)

        except Exception:
            stats.update({
                'conversations': 0,
                'sessions': 0,
                'code_analyses': 0,
                'database_size_mb': 0
            })

        if self.available:
            try:
                memory = psutil.virtual_memory()
                stats.update({
                    'system_memory_total_gb': round(memory.total / (1024 ** 3), 2),
                    'system_memory_used_gb': round(memory.used / (1024 ** 3), 2),
                    'system_memory_percent': round(memory.percent, 1)
                })
            except Exception:
                pass

        return stats

    def get_disk_usage_details(self) -> Dict[str, Any]:
        """Get detailed disk usage information"""
        if not self.available:
            return {'error': 'System monitoring not available'}

        try:
            partitions = psutil.disk_partitions()
            disk_info = {}

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total_gb': round(usage.total / (1024 ** 3), 2),
                        'used_gb': round(usage.used / (1024 ** 3), 2),
                        'free_gb': round(usage.free / (1024 ** 3), 2),
                        'usage_percent': round((usage.used / usage.total) * 100, 1)
                    }
                except PermissionError:
                    continue

            return disk_info

        except Exception as e:
            return {'error': f'Disk usage error: {e}'}

    def get_temperature_info(self) -> Dict[str, Any]:
        """Get system temperature information (if available)"""
        if not self.available:
            return {'error': 'System monitoring not available'}

        try:
            temps = psutil.sensors_temperatures()

            if not temps:
                return {'message': 'No temperature sensors found'}

            temp_info = {}
            for name, entries in temps.items():
                temp_info[name] = []
                for entry in entries:
                    temp_info[name].append({
                        'label': entry.label or 'Unknown',
                        'current': entry.current,
                        'high': entry.high,
                        'critical': entry.critical
                    })

            return temp_info

        except AttributeError:
            return {'message': 'Temperature monitoring not supported on this platform'}
        except Exception as e:
            return {'error': f'Temperature info error: {e}'}

    def get_optimization_suggestions(self) -> List[str]:
        """Get system optimization suggestions based on current state"""
        if not self.available:
            return ["Install psutil for system monitoring: pip install psutil"]

        suggestions = []

        try:
            metrics = self.get_system_metrics()

            if 'error' in metrics:
                return suggestions

            if metrics['cpu']['usage_percent'] > 80:
                suggestions.append("High CPU usage detected - consider closing unnecessary applications")

                top_processes = self.get_process_info(5)
                if top_processes:
                    high_cpu_processes = [p['name'] for p in top_processes if p['cpu_percent'] > 10]
                    if high_cpu_processes:
                        suggestions.append(f"High CPU processes: {', '.join(high_cpu_processes[:3])}")

            if metrics['memory']['usage_percent'] > 85:
                suggestions.append("High memory usage - consider adding more RAM or closing applications")

            if metrics['disk']['usage_percent'] > 90:
                suggestions.append("Very low disk space - clean up files immediately")
                suggestions.append("Consider moving large files to external storage")
            elif metrics['disk']['usage_percent'] > 80:
                suggestions.append("Low disk space - consider cleaning up temporary files")

            if metrics['system']['uptime_hours'] > 168:
                suggestions.append("System uptime >1 week - consider restarting to apply updates")

            db_stats = self.get_memory_stats()
            if db_stats.get('database_size_mb', 0) > 100:
                suggestions.append("Large Sarek database - consider cleaning old conversations")

            if not suggestions:
                suggestions.append("System appears to be running optimally!")

        except Exception:
            suggestions.append("Unable to analyze system for optimization suggestions")

        return suggestions