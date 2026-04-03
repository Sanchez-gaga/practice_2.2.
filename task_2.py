import os
import shutil
import time
import subprocess
import platform

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_cpu_usage():
    system = platform.system()
    if system == "Linux":
        # Читаем /proc/stat
        with open("/proc/stat", "r") as f:
            line = f.readline()
        parts = line.split()
        user = int(parts[1])
        nice = int(parts[2])
        system = int(parts[3])
        idle = int(parts[4])
        total = user + nice + system + idle
        return round((1 - idle / total) * 100, 1)
    elif system == "Windows":
        try:
            result = subprocess.run(
                ["wmic", "cpu", "get", "loadpercentage", "/format:value"],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.splitlines():
                if line.startswith("LoadPercentage="):
                    return int(line.split("=")[1])
        except:
            pass
        return 0
    else:
        return 0  

def get_memory_usage():
    system = platform.system()
    if system == "Linux":
        with open("/proc/meminfo", "r") as f:
            meminfo = {}
            for line in f:
                key, value = line.split(":", 1)
                meminfo[key] = int(value.split()[0]) * 1024  # в байты
        total = meminfo.get("MemTotal", 0)
        available = meminfo.get("MemAvailable", 0)
        used = total - available
        percent = (used / total) * 100 if total else 0
        return used, total, percent
    elif system == "Windows":
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/format:value"],
                capture_output=True, text=True, timeout=2
            )
            total_kb = None
            free_kb = None
            for line in result.stdout.splitlines():
                if line.startswith("TotalVisibleMemorySize="):
                    total_kb = int(line.split("=")[1])
                elif line.startswith("FreePhysicalMemory="):
                    free_kb = int(line.split("=")[1])
            if total_kb and free_kb:
                total = total_kb * 1024
                used = (total_kb - free_kb) * 1024
                percent = (used / total) * 100
                return used, total, percent
        except:
            pass
        return 0, 0, 0
    else:
        return 0, 0, 0

def get_disk_usage(path='/'):
    usage = shutil.disk_usage(path)
    percent = (usage.used / usage.total) * 100
    return usage.used, usage.total, percent

def format_bytes(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"

def main():
    print("=== Системный монитор (без psutil) ===")
    print("Для выхода нажмите Ctrl+C\n")
    
    if platform.system() == "Windows":
        disk_path = 'C:\\'
    else:
        disk_path = '/'
    
    try:
        while True:
            clear_screen()
            print("=== Системный монитор ===")
            print(f"Обновление каждые 2 секунды | Ctrl+C для выхода\n")
            
            cpu = get_cpu_usage()
            print(f"📊 ЗАГРУЗКА CPU: {cpu}%\n")
            
            used_ram, total_ram, ram_percent = get_memory_usage()
            if total_ram:
                print(f"💾 ОПЕРАТИВНАЯ ПАМЯТЬ:")
                print(f"   Использовано: {format_bytes(used_ram)}")
                print(f"   Всего: {format_bytes(total_ram)}")
                print(f"   Загруженность: {ram_percent:.1f}%\n")
            else:
                print(f"💾 ОПЕРАТИВНАЯ ПАМЯТЬ: не удалось получить данные\n")
            
            used_disk, total_disk, disk_percent = get_disk_usage(disk_path)
            print(f"💿 ДИСК {disk_path}:")
            print(f"   Использовано: {format_bytes(used_disk)}")
            print(f"   Всего: {format_bytes(total_disk)}")
            print(f"   Загруженность: {disk_percent:.1f}%\n")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\nМониторинг завершён.")

if __name__ == "__main__":
    main()
