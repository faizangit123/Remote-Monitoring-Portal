"""
System Data Collector
Uses psutil to collect all system information from the Windows machine.
This is the "eyes" of the agent — it sees everything on the system.
"""

import psutil
import platform
import socket
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SystemCollector:
    def __init__(self):
        """Initialize collector with cached static data."""
        self._static_info = None

    # ===========================================================
    # MAIN COLLECTION METHOD
    # ===========================================================

    def collect_all(self) -> Dict[str, Any]:
        """
        Collect ALL system data in one call.

        Returns a dictionary with:
        - system_info: OS, hostname, CPU model (static)
        - cpu: Current CPU usage
        - memory: Current RAM usage
        - disk: Disk partitions and usage
        - network: Network interfaces and connections
        - users: Logged-in users

        Returns:
            Dict with all system data
        """
        try:
            data = {
                # Static info (OS, hostname, CPU model)
                **self._get_static_info(),

                # Dynamic info (changes every collection)
                "cpu_usage_percent": self._get_cpu_usage(),
                "ram_used_gb": self._get_ram_used(),
                "ram_usage_percent": self._get_ram_percent(),
                "disk_used_gb": self._get_disk_used(),
                "disk_usage_percent": self._get_disk_percent(),
                "uptime_hours": self._get_uptime_hours(),
                "ip_address": self._get_ip_address(),

                # Timestamp of when data was collected
                "collected_at": datetime.now(timezone.utc).isoformat()
            }
            return data

        except Exception as e:
            logger.error(f"Error collecting system data: {e}")
            return {"error": str(e), "collected_at": datetime.now(timezone.utc).isoformat()}

    # ===========================================================
    # STATIC SYSTEM INFO (cached, doesn't change)
    # ===========================================================

    def _get_static_info(self) -> Dict[str, Any]:
        """
        Get static system information (only reads once, then cached).

        Static means it doesn't change while the computer is running:
        - OS name and version
        - CPU model and core count
        - Total RAM
        - Total disk space
        - Hostname
        """
        if self._static_info is not None:
            return self._static_info  # Return cached version

        try:
            # --- Operating System ---
            os_info = platform.uname()
            os_name = f"{os_info.system} {os_info.release}"

            os_version = os_info.version


            # --- Hostname ---
            hostname = socket.gethostname()

            # --- CPU ---
            cpu_model = self._get_cpu_model()

            cpu_cores = psutil.cpu_count(logical=True)

            cpu_physical_cores = psutil.cpu_count(logical=False)

            # --- RAM ---
            ram_info = psutil.virtual_memory()
            ram_total_gb = round(ram_info.total / (1024 ** 3), 2)


            # --- Disk ---
            disk_total_gb, _ = self._get_disk_totals()

            self._static_info = {
                "os_name": os_name,
                "os_version": os_version,
                "hostname": hostname,
                "cpu_model": cpu_model,
                "cpu_cores": cpu_cores,
                "cpu_physical_cores": cpu_physical_cores,
                "ram_total_gb": ram_total_gb,
                "disk_total_gb": disk_total_gb,
                "architecture": os_info.machine,
            }
            return self._static_info

        except Exception as e:
            logger.error(f"Error getting static info: {e}")
            return {}

    def _get_cpu_model(self) -> str:
        """Get CPU model name."""
        try:
            # Try Windows-specific method first
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            )
            cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            return cpu_name.strip()
        except Exception:
            # Fallback: use platform module
            return platform.processor()

    def _get_disk_totals(self):
        """Get total disk space across all partitions."""
        try:
            total_gb = 0
            total_used_gb = 0
            for partition in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb += usage.total / (1024 ** 3)
                    total_used_gb += usage.used / (1024 ** 3)
                except (PermissionError, OSError):
                    continue  # Skip inaccessible partitions

            return round(total_gb, 2), round(total_used_gb, 2)
        except Exception:
            return 0.0, 0.0

    # ===========================================================
    # DYNAMIC SYSTEM DATA (changes every collection)
    # ===========================================================

    def _get_cpu_usage(self) -> float:
        """
        Get current CPU usage percentage.

        interval=1 means: measure CPU for 1 second to get accurate reading.
        Without interval, psutil returns 0.0 on first call.
        """
        try:
            usage = psutil.cpu_percent(interval=1)
            return round(usage, 1)
        except Exception:
            return 0.0

    def _get_ram_used(self) -> float:
        """Get current RAM used in GB."""
        try:
            ram = psutil.virtual_memory()
            return round(ram.used / (1024 ** 3), 2)
        except Exception:
            return 0.0

    def _get_ram_percent(self) -> float:
        """Get current RAM usage percentage."""
        try:
            return round(psutil.virtual_memory().percent, 1)
        except Exception:
            return 0.0

    def _get_disk_used(self) -> float:
        """Get total disk space used in GB across all drives."""
        try:
            _, used = self._get_disk_totals()
            return used
        except Exception:
            return 0.0

    def _get_disk_percent(self) -> float:
        """Get overall disk usage percentage."""
        try:
            total_gb, used_gb = self._get_disk_totals()
            if total_gb == 0:
                return 0.0
            return round((used_gb / total_gb) * 100, 1)
        except Exception:
            return 0.0

    def _get_uptime_hours(self) -> float:
        try:
            boot_timestamp = psutil.boot_time()

            now_timestamp = datetime.now().timestamp()
            uptime_seconds = now_timestamp - boot_timestamp
            uptime_hours = uptime_seconds / 3600  # Convert seconds → hours

            return round(uptime_hours, 2)
        except Exception:
            return 0.0

    def _get_ip_address(self) -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))

                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    # ===========================================================
    # PROCESSES
    # ===========================================================

    def collect_processes(self) -> List[Dict[str, Any]]:
        processes = []

        procs = list(psutil.process_iter(['pid', 'name', 'status', 'username']))
        for proc in procs:
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        import time
        time.sleep(0.5)

        for proc in procs:
            try:
                # Get process info
                info = proc.as_dict(
                    attrs=['pid', 'name', 'status', 'username', 'cpu_percent', 'memory_info']
                )

                memory_mb = 0.0
                if info.get('memory_info'):
                    memory_mb = round(info['memory_info'].rss / (1024 * 1024), 2)


                processes.append({
                    "pid": info.get('pid', 0),
                    "name": info.get('name', 'Unknown'),
                    "cpu_percent": round(info.get('cpu_percent', 0.0) or 0.0, 2),
                    "memory_mb": memory_mb,
                    "status": info.get('status', 'unknown'),
                    "username": info.get('username', 'N/A')
                })

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process ended while we were reading it — skip it
                continue
            except Exception as e:
                logger.debug(f"Process read error: {e}")
                continue

        # Sort by CPU usage, highest first
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)

        logger.info(f"Collected {len(processes)} processes")
        return processes

    # ===========================================================
    # DISK PARTITIONS (detailed)
    # ===========================================================

    def collect_disk_partitions(self) -> List[Dict[str, Any]]:
        partitions = []

        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                partitions.append({
                    "device": partition.device,

                    "mountpoint": partition.mountpoint,

                    "fstype": partition.fstype,

                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "usage_percent": round(usage.percent, 1)
                })

            except (PermissionError, OSError):
                continue

        return partitions

    # ===========================================================
    # NETWORK INFORMATION
    # ===========================================================

    def collect_network_info(self) -> Dict[str, Any]:
        """
        Collect network interface information and connection stats.

        Returns:
            Dict with:
            - interfaces: list of network interfaces with IP/MAC
            - stats: bytes sent/received totals
        """
        try:
            interfaces = []

            # Get all network interfaces
            net_addrs = psutil.net_if_addrs()

            for interface_name, addresses in net_addrs.items():
                interface_info = {"name": interface_name, "addresses": []}

                for addr in addresses:
                    addr_info = {
                        "address": addr.address,
                        "family": str(addr.family)
                    }
                    if addr.netmask:
                        addr_info["netmask"] = addr.netmask
                    interface_info["addresses"].append(addr_info)

                interfaces.append(interface_info)

            # Get network I/O statistics
            net_io = psutil.net_io_counters()
            stats = {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024 * 1024), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024 * 1024), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }

            return {
                "interfaces": interfaces,
                "stats": stats
            }

        except Exception as e:
            logger.error(f"Error collecting network info: {e}")
            return {"interfaces": [], "stats": {}}

    # ===========================================================
    # SYSTEM USERS
    # ===========================================================

    def collect_users(self) -> List[Dict[str, Any]]:
        try:
            users = []
            for user in psutil.users():
                users.append({
                    "username": user.name,
                    "terminal": user.terminal or "console",
                    "host": user.host or "localhost",
                    "started": datetime.fromtimestamp(user.started).isoformat()
                })
            return users
        except Exception as e:
            logger.error(f"Error collecting users: {e}")
            return []

    # ===========================================================
    # INSTALLED APPLICATIONS (Windows only)
    # ===========================================================

    def collect_installed_apps(self) -> List[Dict[str, Any]]:
        apps = []
        try:
            import winreg

            # Registry paths for installed apps (32-bit and 64-bit)
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]

            for reg_path in registry_paths:
                try:
                    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    num_subkeys = winreg.QueryInfoKey(registry_key)[0]

                    for i in range(num_subkeys):
                        try:
                            subkey_name = winreg.EnumKey(registry_key, i)
                            subkey = winreg.OpenKey(registry_key, subkey_name)

                            try:
                                name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                if not name or not name.strip():
                                    continue  # Skip entries without a name

                                app = {"name": name.strip()}

                                # Try to get version (optional)
                                try:
                                    version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                                    app["version"] = version
                                except Exception:
                                    app["version"] = "N/A"

                                # Try to get publisher (optional)
                                try:
                                    publisher, _ = winreg.QueryValueEx(subkey, "Publisher")
                                    app["publisher"] = publisher
                                except Exception:
                                    app["publisher"] = "N/A"

                                apps.append(app)

                            except FileNotFoundError:
                                pass  # No DisplayName — skip this entry

                        except Exception:
                            continue

                except Exception:
                    continue

            # Remove duplicates by name
            seen = set()
            unique_apps = []
            for app in apps:
                if app["name"] not in seen:
                    seen.add(app["name"])
                    unique_apps.append(app)

            # Sort alphabetically
            unique_apps.sort(key=lambda x: x["name"].lower())

            logger.info(f"Found {len(unique_apps)} installed applications")
            return unique_apps

        except Exception as e:
            logger.error(f"Error reading installed apps: {e}")
            return []


# ===========================================================
# QUICK TEST
# ===========================================================

if __name__ == "__main__":
    import json

    print("=" * 60)
    print("SYSTEM COLLECTOR TEST")
    print("=" * 60)

    collector = SystemCollector()

    print("\n📊 System Overview:")
    data = collector.collect_all()
    for key, value in data.items():
        print(f"  {key}: {value}")

    print("\n💾 Disk Partitions:")
    for part in collector.collect_disk_partitions():
        print(f"  {part['device']} → {part['used_gb']}GB / {part['total_gb']}GB ({part['usage_percent']}%)")

    print("\n🌐 Network:")
    net = collector.collect_network_info()
    print(f"  Sent: {net['stats'].get('bytes_sent_mb', 0)} MB")
    print(f"  Recv: {net['stats'].get('bytes_recv_mb', 0)} MB")

    print("\n👤 Users:")
    for user in collector.collect_users():
        print(f"  {user['username']} on {user['terminal']}")

    print("\n⚙️ Top 5 Processes by CPU:")
    processes = collector.collect_processes()
    for proc in processes[:5]:
        print(f"  [{proc['pid']}] {proc['name']} - CPU: {proc['cpu_percent']}% - RAM: {proc['memory_mb']}MB")

    print("\n✅ Collector test complete!")
    print("=" * 60)