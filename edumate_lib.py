import requests
import json
import time

def get_time():
    text = requests.get("http://just-the-time.appspot.com/").text.strip()
    m_time = time.strptime(text, "%Y-%m-%d %H:%M:%S")
    return(m_time)

def time_adj(m_time):
    year = m_time.tm_year
    month = m_time.tm_mon
    day = m_time.tm_mday
    hours = m_time.tm_hour + 11
    mins = m_time.tm_min
    secs = m_time.tm_min

    if hours > 24:
        hours -= 24
        day += 1
    if month == 2 and day > 28:
        day -= 28
        month += 1
    elif month in [4,6,9,11] and day > 30:
        day -= 30
        month += 1
    elif day > 31:
        day -= 31
        month += 1

    m_time = time.struct_time((year, month, day, hours, mins, secs, m_time.tm_wday, m_time.tm_yday, m_time.tm_isdst))
    return(m_time)

def make_obj(data):
    m_time = get_time()
    new_data = []
    for entry in data:
        new_entry = {}
        include = True
        for attribute in entry:
            if attribute == "start":
                try:
                    obj = time.strptime(entry["start"], "%Y%m%dT%H%M%SZ")
                    new_entry["start"] = time_adj(obj)
                except:
                    include = False
            elif attribute == "end":
                try:
                    obj = time.strptime(entry["end"], "%Y%m%dT%H%M%SZ")
                    if obj < m_time:
                        include = False
                    new_entry["end"] = time_adj(obj)
                except:
                    include = False
            else:
                new_entry[attribute] = entry[attribute]
        if include:
            new_data.append(new_entry)
    return(new_data)

def time_sort(data,num):
    new_data = []
    for entry1 in data:
        new_new_data = []
        added = False
        for entry2 in new_data:
            if entry2["start"] < entry1["start"]:
                new_new_data.append(entry2)
            else:
                if not added:
                    new_new_data.append(entry1)
                new_new_data.append(entry2)
                added = True
        if not added:
            new_new_data.append(entry1)
        new_data = new_new_data
    return(new_data[0:num])

def remove_obj(data):
    new_data = []
    for entry in data:
        new_entry = {}
        for attribute in entry:
            if attribute == "start":
                new_entry["start"] = time.strftime("%d/%m/%Y %H:%M:%S",entry["start"])
            elif attribute == "end":
                new_entry["end"] = time.strftime("%d/%m/%Y %H:%M:%S",entry["end"])
            else:
                new_entry[attribute] = entry[attribute]
        new_data.append(new_entry)
    return(new_data)

def get_timetable(auth_string,num):
    url = "https://edumate.sacs.nsw.edu.au/sacs4/cal.php/calendar"
    headers = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-encoding":"gzip, deflate, br",
        "Accept-language":"en-US,en;q=0.9",
        "Authorization":auth_string,
        "Cache-Control":"max-age=0",
        "Connection":"keep-alive",
        "Host":"edumate.sacs.nsw.edu.au",
        "sec-ch-ua":"\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform":"\"Windows\"",
    }
    response = requests.get(url, headers=headers)

    timetable_data = []

    event_data = {}

    for line in response.text.split("\n"):
        if "END:VEVENT" in line:
            timetable_data.append(event_data)
            event_data  = {}
        elif "SUMMARY" in line:
            data = line.split(":")[1]
            event_data["period"] = data[1]
            data = data.split(" - ")
            event_data["class"] = data[0][3:]
            try:
                event_data["teacher"] = data[1].strip()
            except:
                event_data["teacher"] = "NA"
        elif "LOCATION" in line:
            data = line.split(":")
            event_data["location"] = data[1].strip()
        elif "DTSTART" in line:
            data = line.split(":")
            event_data["start"] = data[1].strip()
        elif "DTEND" in line:
            data = line.split(":")
            event_data["end"] = data[1].strip()

    timetable_data = remove_obj(time_sort(make_obj(timetable_data),num))
    return(timetable_data)

#Basic TENhbXBiZWxsMjNAc3R1ZGVudC5zYWNzLm5zdy5lZHUuYXU6MTgyNjg0