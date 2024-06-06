from flask import session
import sqlite3 

# 데이터베이스에 연결
con = sqlite3.connect('database.db')
cursor = con.cursor()

# 데이터 출력
cursor.execute('SELECT * FROM LECTURES')
rows = cursor.fetchall()
# print(*rows, sep="\n" )


def convertFunction(rows, username):
    lectures = []
    for row in range(len(rows)):
        if rows[row][0] == username:
            #한 요일에만 수업 
            day1 = (rows[row][4].split())[1] #09:00-12:50
            time1 = (day1.split('-'))[0]
            time2 = (day1.split('-'))[1]

            hour1 = int((time1.split(':'))[0])
            minute1 = int((time1.split(':'))[1])

            hour2 = int((time2.split(':'))[0])
            minute2 = int((time2.split(':'))[1])

            minuteDifference = minute2 - minute1
            hourDifference = hour2 - hour1

            if minuteDifference < 0:
                minuteDifference += 60
                hourDifference -= 1

            hourToMinuteDifference = hourDifference * 60
            difference = hourToMinuteDifference + minuteDifference
            unit = int(difference / 5)

            start_index = (hour1 - 9)*12 + minute1/6
            lectures.append([rows[row][2], rows[row][3], (rows[row][4].split())[0], (day1.split('-'))[0], (day1.split('-'))[1], unit, start_index, rows[row][1] ])

        #일주일에 수업 2번일때
        
            if rows[row][5] != "":
                day2 = (rows[row][5].split())[1] #09:00-12:50
                time1 = (day2.split('-'))[0]
                time2 = (day2.split('-'))[1]

                hour1 = int((time1.split(':'))[0])
                minute1 = int((time1.split(':'))[1])

                hour2 = int((time2.split(':'))[0])
                minute2 = int((time2.split(':'))[1])

                minuteDifference = minute2 - minute1
                hourDifference = hour2 - hour1

                if minuteDifference < 0:
                    minuteDifference += 60
                    hourDifference -= 1

                hourToMinuteDifference = hourDifference * 60
                difference = hourToMinuteDifference + minuteDifference
                unit = int(difference / 5)

                start_index = (hour1 - 9)*12 + minute1/6


                lectures.append([rows[row][2], rows[row][3], (rows[row][5].split())[0], (day2.split('-'))[0], (day2.split('-'))[1], unit, start_index, rows[row][1] ])
    
    

    return lectures

def create_timetable(lectures):
    timetable = {day: [''] * ((19 - 9) * 12) for day in ['월', '화', '수', '목', '금']}
    for lecture in lectures:
        subject, teacher, days, start_time, end_time, unit, start_index, number = lecture
        start_hour, start_minute = map(int, start_time.split(':'))
        end_hour, end_minute = map(int, end_time.split(':'))

        if start_hour < 9:
            start_hour, start_minute = 9, 0
        if end_hour > 19:
            end_hour, end_minute = 19, 0

        start_index = (start_hour - 9) * 12 + start_minute // 5
        end_index = start_index + unit

        for day in days.split():
            for i in range(start_index, end_index):
                timetable[day][i] = {
                    'number': number,
                    'subject': subject,
                    'teacher': teacher,
                    'unit': unit,
                }

    return timetable

def getSubjectNumber(rows, username):
    check =  []
    for row in range(len(rows)):
        if rows[row][0] == username:
            check.append(rows[row][1])
    return check




# 연결 종료
con.close()

