import sqlite3
import csv

conn = sqlite3.connect('database.db')
print('Opened database successfully')

# MEMBERS 테이블 생성
conn.execute('''
CREATE TABLE IF NOT EXISTS MEMBERS (
    ID TEXT PRIMARY KEY,
    PW TEXT,
    EMAIL TEXT,
    USERNAME TEXT,
    NICKNAME TEXT,
    PROFILE_PIC TEXT DEFAULT 'profile.png'
)
''')
print ('Table MEMBERS created successfully')

# LECTURES 테이블 생성
conn.execute('''
CREATE TABLE IF NOT EXISTS LECTURES (
    USER_ID TEXT,
    ID TEXT,
    NAME TEXT,
    PROF TEXT,
    TIME1 TEXT,
    TIME2 TEXT,
    CREDITS TEXT,
    YEAR TEXT,
    PRIMARY KEY (USER_ID, ID),
    FOREIGN KEY (USER_ID) REFERENCES MEMBERS(ID)
)
''')
print ('Table LECTURES created successfully')

# TOTALLECTURES 테이블 생성
conn.execute('''
CREATE TABLE IF NOT EXISTS TOTALLECTURES (
    ID TEXT,
    NAME TEXT,
    PROF TEXT,
    TIME1 TEXT,
    TIME2 TEXT,
    CREDITS TEXT,
    YEAR TEXT
)
''')
print('Table TOTALLECTURES created successfully')

# MEMINFO 테이블 생성
conn.execute('''
CREATE TABLE IF NOT EXISTS MEMINFO (
    MEM_ID TEXT PRIMARY KEY,
    MEM_NAME TEXT,
    MEM_NICKNAME TEXT,
    MEM_INTRO TEXT,
    MEM_YEAR TEXT,
    MEM_SEX TEXT,
    MEM_MAJ_1 TEXT,
    MEM_MAJ_2 TEXT,
    FOREIGN KEY (MEM_ID) REFERENCES MEMBERS(ID)
)
''')
print ('Table MEMINFO created successfully')

#MESSAGE 테이블 생성--- 혜빈
conn.execute('''
CREATE TABLE IF NOT EXISTS MESSAGE (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    SENDER_ID TEXT,
    RECIPIENT_ID TEXT,
    MESSAGE TEXT,
    TIMESTAMP TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SENDER_ID) REFERENCES MEMBERS(ID),
    FOREIGN KEY (RECIPIENT_ID) REFERENCES MEMBERS(ID)
)
''')
print('Table MESSAGE created successfully')

# FRIEND 테이블 생성
conn.execute('''
CREATE TABLE IF NOT EXISTS FRIEND (
    USER1 TEXT,
    USER2 TEXT,
    FRIEND_STATUS INTEGER DEFAULT 0,
    PRIMARY KEY (USER1, USER2),
    FOREIGN KEY (USER1) REFERENCES MEMBERS(ID),
    FOREIGN KEY (USER2) REFERENCES MEMBERS(ID)
)
''')
print('Table FRIEND created successfully')

# NOTIFICATIONS 테이블 생성
conn.execute('''
CREATE TABLE IF NOT EXISTS NOTIFICATIONS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    USER_ID TEXT,
    SENDER_ID TEXT,
    MESSAGE TEXT,
    SEEN INTEGER DEFAULT 0,
    FOREIGN KEY (USER_ID) REFERENCES MEMBERS(ID),
    FOREIGN KEY (SENDER_ID) REFERENCES MEMBERS(ID)
)
''')
print('Table NOTIFICATIONS created successfully')

conn.close()
# 데이터베이스에 연결
con = sqlite3.connect('database.db')
cursor = con.cursor()

#csv 파일 읽기 및 데이터베이스에 삽입
with open('lectures.csv', 'r') as file:
    csv_data = csv.reader(file)
    next(csv_data) # 첫번째 행은 헤더이므로 건너뜀
    for row in csv_data:
        cursor.execute('INSERT INTO TOTALLECTURES VALUES (?, ?, ?, ?, ?, ?, ?)', row)

print("csv data successfully added")

#변경사항 저장 및 연결 종료
con.commit()
con.close()