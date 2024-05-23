import psutil
from psutil._common import bytes2human
from django.shortcuts import render, redirect
from django.http import request, HttpResponse, JsonResponse
import json
from datetime import datetime
import time
import socket
# Create your views here.

AF_map = {
    psutil.AF_LINK: "MAC",
    socket.AF_INET: "IPv4",
    socket.AF_INET6: "IPv6"
}

duplex_map = {
    psutil.NIC_DUPLEX_HALF: "half",
    psutil.NIC_DUPLEX_FULL: "full",
    psutil.NIC_DUPLEX_UNKNOWN: "unidentified"
}


def homepage(request):
    if request.method == 'POST':
        data = request.POST.get('y')
        date_time = request.POST.get('label')
        # print("DATA:", data, '---', 'datetime', date_time)
        return JsonResponse({'status': 'success'})
    else:
        return render(request, 'home.html')

def cpu_util_per(request):
    cpu_perc = psutil.cpu_percent(interval=1, percpu=False)
    cpu_freq = psutil.cpu_freq()
    date_time = datetime.now()
    data = {'label':date_time.strftime("%H:%M:%S") , 'cpu_percent': cpu_perc, 'cpu_base_freq': cpu_freq.max/10**3, 'cpu_current_freq': cpu_freq.current/10**3}
    return JsonResponse(data)

def memory(request):
    memory_stats = psutil.virtual_memory()
    date_time = datetime.now()
    total_memory = round(memory_stats[0]/1024**3, 2)
    available_memory = round(memory_stats[1]/1024**3,2)
    used_memory = round(memory_stats[3]/1024**3,2)
    percentage = memory_stats[2]
    data = {'label':date_time.strftime("%H:%M:%S"), 'y': available_memory, 'y1': total_memory, 'y2': used_memory, 'y3': percentage}
    return JsonResponse(data)

def diskStorage(request):
    disk_partitions = psutil.disk_partitions(all=True)
    disk_stats = psutil.disk_usage(disk_partitions[1].mountpoint)

    startTime = time.time()
    disk_IO_counter = psutil.disk_io_counters(perdisk=True, nowrap=True)['PhysicalDrive1']
    # print(disk_IO_counter)
    readBytes1 = disk_IO_counter.read_bytes
    writeBytes1 = disk_IO_counter.write_bytes
    readTime1 = disk_IO_counter.read_time
    writeTime1 = disk_IO_counter.write_time

    time.sleep(1)

    disk_IO_counter = psutil.disk_io_counters(perdisk=True, nowrap=True)['PhysicalDrive1']
    readBytes2 = disk_IO_counter.read_bytes
    writeBytes2 = disk_IO_counter.write_bytes
    endTime = time.time()

    readBytes = readBytes2 - readBytes1
    writeBytes = writeBytes2 - writeBytes1

    Tdiff = endTime - startTime
    # read and write speeds in MB/s
    read_speed = (readBytes / Tdiff)/1024**2
    write_speed = (writeBytes /Tdiff)/1024**2

    data = {'totalDisk': disk_stats.total/1024**3, 'usedDisk': disk_stats.used/1024**3, 'freeDisk': disk_stats.free/1024**3, 'percent': disk_stats.percent, 'readSpeed': round(read_speed,4), 'writeSpeed': round(write_speed,4)}

    return JsonResponse(data)

def BatteryStatus(request):
    battery = psutil.sensors_battery()

    mm, ss = divmod(battery.secsleft, 60)
    hh, mm = divmod(mm, 60)
    battery_remain_time = str(hh) + ":" + str(mm) + ":" + str(ss)

    charge_status = ""
    if battery.power_plugged:
        if battery.percent < 100:
            charge_status = "charging"
        else:
            charge_status = "charged"
    else:
        charge_status = "discharging"

    data = {'percent': battery.percent, 'secsleft': battery_remain_time, 'charge_status': charge_status}

    # print(psutil.Process())
    # print(list(psutil.Process().as_dict().keys()))

    # proc = {p.pid: p.info for p in psutil.process_iter(['name', 'username', 'status', 'memory_info', 'cpu_percent'])}
    # print(proc)

    return JsonResponse(data)

def Detail(request):

    return render(request, 'detail_page.html')

def get_cpu_cnt(request):
    cpu = psutil.cpu_count()
    data = {'cpu_count': cpu}
    return JsonResponse(data)

def pid(request):
    proc = {p.pid: p.info for p in psutil.process_iter(['name', 'username', 'status', 'memory_info', 'memory_percent', 'cpu_percent', 'num_threads'])}
    return JsonResponse(proc)

def NetworkDetail(request):
    return render(request, 'network_page.html')

def Network(request):
    start_time = time.time()
    net_io_counters = psutil.net_io_counters(pernic=True, nowrap=True)
    net_io1 = net_io_counters['Wi-Fi']

    time.sleep(3)

    net_io_counters = psutil.net_io_counters(pernic=True, nowrap=True)
    net_io2 = net_io_counters['Wi-Fi']
    end_time = time.time()

    bytes_sent1 = net_io1.bytes_sent
    bytes_recv1 = net_io1.bytes_recv
    bytes_sent2 = net_io2.bytes_sent
    bytes_recv2 = net_io2.bytes_recv

    bytes_sent = bytes_sent2 - bytes_sent1
    bytes_recv = bytes_recv2 - bytes_recv1

    bytes_sent_per_sec = round((bytes_sent/1024),0)
    bytes_recv_per_sec = round((bytes_recv/1024),0)
    total_bytes = bytes_sent2 + bytes_recv2

    data = {'bytes_sent': bytes_sent_per_sec, 'bytes_recv': bytes_recv_per_sec, 'total_bytes': total_bytes}

    net_conn_types = ['tcp', 'udp']
    iterate = 0
    while True:
        get_conn_type = net_conn_types[iterate]
        net_conn = psutil.net_connections(kind=get_conn_type)
        
        # Sorting ALGO
        for i in range(0,len(net_conn)):
            for j in range(i+1, len(net_conn)):
                if (net_conn[i][6] > net_conn[j][6]):
                    temp = net_conn[i]
                    net_conn[i] = net_conn[j]
                    net_conn[j] = temp

        proc_name = []
        for i in range(0, len(net_conn)):
            pid = net_conn[i][6]
            process = psutil.Process(pid=pid).name()
            proc_name.append(process)
        

        data[get_conn_type] = net_conn
        conn_type_proc_nm = get_conn_type + "_process_nm"
        data[conn_type_proc_nm] = proc_name

        iterate += 1

        if iterate == len(net_conn_types):
            break

    return JsonResponse(data)

def NIC(request):
    data = {}
    stats = psutil.net_if_stats()
    for net, addr in psutil.net_if_addrs().items():
        if net in stats:
            length = len(addr)

            duplex = duplex_map[stats[net].duplex]
            data[net] = {'stats': stats[net],'duplex': duplex}

            for i in range(0, length):
                addr_family = AF_map[addr[i].family]
                if addr_family == "MAC":
                    key = addr_family + '_address'
                    data[net][key] = addr[i].address
                elif addr_family == "IPv4":
                    key1 = addr_family + '_address'
                    key2 = addr_family + '_subnet'
                    data[net][key1] = addr[i].address
                    data[net][key2] = addr[i].netmask
                elif addr_family == "IPv6":
                    key = addr_family + '_address'
                    data[net][key] = addr[i].address
    
    io_counters = psutil.net_io_counters(pernic=True, nowrap=True)
    io_keys = list(stats.keys())

    for k in io_keys:
        if stats[k].isup:
            bytes_sent = io_counters[k].bytes_sent
            bytes_recv = io_counters[k].bytes_recv
            data[k]["bytes_sent"] = bytes_sent
            data[k]["bytes_recv"] = bytes_recv

    return JsonResponse(data)