from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify #jsonify추가--- 혜빈
import sqlite3 as sql
import sys
from calculateTime import convertFunction, getSubjectNumber, create_timetable #가영 : 변경
from flask_socketio import SocketIO, join_room, leave_room, send #혜빈
import time

application = Flask(__name__)

application = Flask(__name__)
application.secret_key = "ggi1234"
socketio = SocketIO(application) #혜빈

login = False

@application.route("/")
def start():
    if "userID" in session:
        return render_template("start.html",username = session.get("userID"), login = True)
    else:
        return render_template("start.html",login = False)
    
@application.route("/login", methods = ["POST","get"])
def login():
    _id_ = request.args.get("loginId")
    _password_ = request.args.get("loginPw")
    
    con= sql.connect('database.db')
    cur= con.cursor()
    
    response = con.execute('SELECT EXISTS(SELECT * FROM MEMBERS WHERE ID =? AND PW =?)', (_id_,_password_,))
    fetched = response.fetchone()[0]
    if fetched == 1:
        session["userID"] = _id_
    else:
        flash("아이디와 비밀번호가 올바르지 않습니다") 
    return redirect(url_for("start"))
    
    
@application.route("/hello")
def hello():
    return render_template("hello.html")

@application.route("/logout")
def logout():
    session.pop("userID")
    return redirect(url_for("start"))

@application.route("/regmember",methods=['GET','POST'])
def regMem():
    return render_template("regmember.html")

@application.route("/addmem", methods = ['POST', 'GET'])
def addmem():
    if request.method == 'POST':
        
            id = request.form['id']
            pw = request.form['password1']
            repw = request.form['password2']
            email= request.form['email']
            name = request.form['username']
            nickname = request.form['nickname']
            
            con =sql.connect('database.db')
            cur = con.cursor()
            
            stmt = 'SELECT EXISTS(SELECT EMAIL FROM MEMBERS WHERE EMAIL= ?)'
            response = con.execute(stmt,(email,))
            fetched = response.fetchone()[0]
            
            stmt1 = 'SELECT EXISTS(SELECT ID FROM MEMBERS WHERE ID=?)'
            response1 = con.execute(stmt1,(id,))
            fetched1 = response1.fetchone()[0]
            
            stmt2 = 'SELECT EXISTS(SELECT NICKNAME FROM MEMBERS WHERE NICKNAME=?)'
            response2 = con.execute(stmt2,(nickname,))
            fetched2 = response2.fetchone()[0]
        
            if not (id and pw and repw and email and name and nickname):
                flash("모두 입력해주세요")
                return render_template('regmember.html')
            elif pw != repw:
                flash("비밀번호를 확인해주세요")
                return render_template('regmember.html')
            elif (fetched == 1):
                flash("이미 가입된 이메일입니다")
                return render_template('regmember.html')
            elif (fetched1 == 1):
                flash("이미 존재하는 아이디입니다")
                return render_template('regmember.html')
            elif (fetched2 == 1):
                flash('이미 존재하는 별명입니다')
                return render_template('regmember.html')
            else:
                cur.execute('INSERT INTO MEMBERS (ID, PW, EMAIL, USERNAME, NICKNAME) VALUES (?,?,?,?,?)', (id, pw, email, name, nickname,))
                cur.execute('INSERT INTO MEMINFO (MEM_ID, MEM_NAME, MEM_NICKNAME) VALUES (?,?,?)',(id, name, nickname,))
                con.commit()
                flash('회원 가입 완료! 로그인해서 겹강이를 이용해보세요!')
                con.close()
                #return render_template('reg_result.html', comment = comment)
                return render_template('start.html')
    else: return ""


@application.route("/home")
def home():
    return render_template("home.html")

@application.route("/friend") #혜빈
def friend():
    user_id = session.get("userID")
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    
    cur.execute('''
   SELECT L.NAME as lecture_name, M.ID as user_id, M.USERNAME as username, 
           M.FRIEND_ACTIVE as friend_active
    FROM LECTURES L
    JOIN MEMBERS M ON L.USER_ID = M.ID
    WHERE L.ID IN (
        SELECT ID
        FROM LECTURES
        WHERE USER_ID = ?
    )
    AND L.USER_ID != ?
    ''', (user_id, user_id))
    
    friends = cur.fetchall()
    con.close()

    friend_dict = {}
    for row in friends:
        lecture_name = row['lecture_name']
        if lecture_name not in friend_dict:
            friend_dict[lecture_name] = []
        friend_dict[lecture_name].append({
            'id': row['user_id'],
            'name': row['username'],
            'friend_active': row['friend_active']
        })

    return render_template("friend_list.html", friend_dict=friend_dict)

@application.route("/accept_friend", methods=["POST"])
def accept_friend():
    user_id = session.get("userID")
    friend_id = request.form["friend_id"]
    
    con = sql.connect('database.db')
    cur = con.cursor()
    
    try:
        # 기존 친구 관계 확인
        cur.execute('SELECT FRIEND_STATUS FROM FRIEND WHERE (USER1 = ? AND USER2 = ?) OR (USER1 = ? AND USER2 = ?)', 
                    (user_id, friend_id, friend_id, user_id))
        row = cur.fetchone()
        
        if row:
            if row[0] == 0:
                # 친구 상태 업데이트
                cur.execute('UPDATE FRIEND SET FRIEND_STATUS = 1 WHERE (USER1 = ? AND USER2 = ?) OR (USER1 = ? AND USER2 = ?)', 
                            (user_id, friend_id, friend_id, user_id))
            elif row[0] == 1:
                # 이미 친구 신청이 있는 경우 알림 추가
                cur.execute('INSERT INTO NOTIFICATIONS (USER_ID, SENDER_ID, MESSAGE) VALUES (?, ?, ?)',
                            (friend_id, user_id, "상대방이 이미 친구신청을 요청하였습니다."))
            elif row[0] == 2:
                # 이미 친구 관계인 경우 알림 추가
                cur.execute('INSERT INTO NOTIFICATIONS (USER_ID, SENDER_ID, MESSAGE) VALUES (?, ?, ?)',
                            (user_id, friend_id, "이미 서로 친구관계입니다."))
        else:
            # 새로운 친구 관계 추가
            cur.execute('INSERT INTO FRIEND (USER1, USER2, FRIEND_STATUS) VALUES (?, ?, 1)', (user_id, friend_id))
        
        con.commit()
        response = {"success": True}
    except Exception as e:
        con.rollback()
        response = {"success": False, "error": str(e)}
    finally:
        con.close()
    
    return jsonify(response)

# SocketIO 이벤트
@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    sender_id = session.get("userID")
    recipient_id = room  # room 이름을 recipient_id로 사용
    
    con = sql.connect('database.db')
    cur = con.cursor()
    cur.execute('INSERT INTO MESSAGE (SENDER_ID, RECIPIENT_ID, MESSAGE) VALUES (?, ?, ?)', 
                (sender_id, recipient_id, message))
    con.commit()
    con.close()
    
    send(data, to=room)

@socketio.on('join')
def handle_join(data):
    join_room(data['room'])

@socketio.on('leave')
def handle_leave(data):
    leave_room(data['room'])

@application.route("/friend_list")
def friend_list():
    user_id = session.get("userID")
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    
    cur.execute('''
    SELECT M.ID, M.USERNAME,
           COALESCE(F.FRIEND_STATUS, 0) AS friend_status
    FROM MEMBERS M
    LEFT JOIN FRIEND F ON (M.ID = F.USER1 AND F.USER2 = ?) OR (M.ID = F.USER2 AND F.USER1 = ?)
    WHERE M.ID != ?
    ''', (user_id, user_id, user_id))
    
    friends = cur.fetchall()
    con.close()

    friend_list = [{'id': row['ID'], 'name': row['USERNAME'], 'friend_status': row['friend_status']} for row in friends]
    
    return render_template("friend_list.html", friends=friend_list)

@application.route("/realfriend_list")
def realfriend_list():
    user_id = session.get("userID")
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    
    # 알림 확인 및 사용자 이름 가져오기
    cur.execute('''
    SELECT N.SENDER_ID, N.MESSAGE, M.USERNAME AS SENDER_NAME
    FROM NOTIFICATIONS N
    JOIN MEMBERS M ON N.SENDER_ID = M.ID
    WHERE N.USER_ID = ? AND N.SEEN = 0
    ''', (user_id,))
    notifications = cur.fetchall()
    
    # 알림을 본 상태로 업데이트
    cur.execute('UPDATE NOTIFICATIONS SET SEEN = 1 WHERE USER_ID = ?', (user_id,))
    con.commit()
    
    # 수락대기 친구 리스트 가져오기
    cur.execute('''
    SELECT M.ID, M.USERNAME
    FROM FRIEND F
    JOIN MEMBERS M ON (M.ID = F.USER1 OR M.ID = F.USER2)
    WHERE (F.USER1 = ? OR F.USER2 = ?) AND F.FRIEND_STATUS = 1 AND M.ID != ?
    ''', (user_id, user_id, user_id))
    pending_friends = cur.fetchall()
    
    # 수락된 친구 리스트 가져오기
    cur.execute('''
    SELECT M.ID, M.USERNAME
    FROM FRIEND F
    JOIN MEMBERS M ON (M.ID = F.USER1 OR M.ID = F.USER2)
    WHERE (F.USER1 = ? OR F.USER2 = ?) AND F.FRIEND_STATUS = 2 AND M.ID != ?
    ''', (user_id, user_id, user_id))
    accepted_friends = cur.fetchall()
    
    con.close()

    pending_friend_list = [{'id': row['ID'], 'name': row['USERNAME']} for row in pending_friends]
    accepted_friend_list = [{'id': row['ID'], 'name': row['USERNAME']} for row in accepted_friends]
    notifications_list = [{'sender_id': row['SENDER_ID'], 'message': row['MESSAGE'], 'sender_name': row['SENDER_NAME']} for row in notifications]

    return render_template("realfriend_list.html", pending_friends=pending_friend_list, accepted_friends=accepted_friend_list, notifications=notifications_list)

@application.route("/friend_profile") #가영
def friend_profile():

    friend_id = request.args.get('friend_id')
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    
    #누구의 프로필인지 추출
    cur = con.cursor()
    cur.execute('SELECT * FROM MEMINFO WHERE MEM_ID=?',(friend_id,))
    row = cur.fetchone()

    #내 시간표 추출
    user_id = session.get("userID")
    cur.execute('SELECT * FROM LECTURES')
    my_rows = cur.fetchall()
    cur.execute('SELECT SUM(CREDITS) FROM LECTURES')
    my_check = getSubjectNumber(my_rows, user_id) #가영 

    #상대 시간표
    cur.execute('SELECT * FROM LECTURES')
    rows = cur.fetchall()
    cur.execute('SELECT SUM(CREDITS) FROM LECTURES')
    totalCredits = cur.fetchone()
    timetable = create_timetable(convertFunction(rows, friend_id)) # 가영 : 추가
    check = getSubjectNumber(rows, friend_id) #가영 

    con.close()
    
    return render_template('friend_profile.html', row=row, rows = rows, result = timetable, check =check, my_check=my_check)


@application.route("/findfriend") #혜빈
def findfriend():
    return redirect(url_for("findfriend_home"))

@application.route('/findfriend_home')
def findfriend_home():
    return render_template('findfriend_home.html')

@application.route('/enternew')
def enternew():
    return render_template('16_search.html')

@application.route('/addsubject', methods = ['POST','GET'])
def addsubject():
    if request.method == 'POST':
        try :
            chosen = request.form['subject']
            with sql.connect('database.db') as con :
                cur = con.cursor()
                con.row_factory = sql.Row
                ##cur.execute('INSERT INTO LECTURES SELECT * FROM TOTALLECTURES WHERE ID = ?',(chosen,))
                ##여기서부터, 과목추가 할 때마다 회원id,total lectures 스키마 그대로 추가
                cur.execute('SELECT * FROM TOTALLECTURES WHERE ID = ?',(chosen,))
                rows = cur.fetchone()
                cur.execute('INSERT INTO LECTURES(USER_ID, ID, NAME, PROF, TIME1, TIME2, CREDITS, YEAR) VALUES(?,?,?,?,?,?,?,?)', (session["userID"], rows[0], rows[1],rows[2],rows[3],rows[4],rows[5],rows[6],))
                con.commit()
                flash('과목이 시간표에 추가되었습니다')
                con.close()
        except:
            con.rollback()
            flash('오류...다시 시도하세요:(')
        finally:
            return redirect(url_for("list"))
    return ''
    
@application.route('/delsubject', methods=['POST'])
def delsubject():
    con= sql.connect('database.db')
    cur= con.cursor()
    del_stmt ='DELETE FROM LECTURES WHERE ID =?'
    cur.execute(del_stmt, [request.form['id']])
    con.commit()
    flash('과목이 시간표에서 삭제되었습니다')
    return redirect(url_for("list"))

@application.route("/search", methods=("GET", "POST"))
def search():
    con = sql.connect('database.db')  # DB와 연결
    con.row_factory = sql.Row
    cur = con.cursor()
    
    if request.method == "POST":  # POST request라면,
        query = request.form["query"]  # "query" 입력칸에서 받은 글자
        stmt = "SELECT * FROM TOTALLECTURES WHERE NAME = ?"
        cur.execute(stmt,(query,))
        rows = cur.fetchall()
        return render_template("16_search_result.html", rows = rows)

@application.route("/timetable")
def list():
    username = session.get("userID")

    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM LECTURES')
    rows = cur.fetchall()
    cur.execute('SELECT SUM(CREDITS) FROM LECTURES')
    totalCredits = cur.fetchone()
    timetable = create_timetable(convertFunction(rows, username)) # 가영 : 추가
    check = getSubjectNumber(rows, username) #가영 
    con.close()
    return render_template('16_timetable.html', rows = rows, totalCredits = totalCredits, result = timetable, check =check, username=username) # 가영

@application.route("/myprofile")
def myprof():
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    
    cur = con.cursor()
    cur.execute('SELECT * FROM MEMINFO WHERE MEM_ID=?',(session["userID"],))
    row = cur.fetchone()
    con.close()
    return render_template('myprof_home.html', row = row)

@application.route('/enternewprof')
def new_profile():
    return render_template('myprof_rev.html')

@application.route("/updateprof",methods = ['POST', 'GET'])
def updateprof():
    if request.method == 'POST':
        try :
            nickname = request.form['nickname']
            intro = request.form['intro']
            year = request.form['year']
            sex = request.form['sex']
            major1 = request.form['major1']
            major2 = request.form['major2']
            
            with sql.connect('database.db') as con :
                cur = con.cursor()
                
                cur.execute('UPDATE MEMBERS SET NICKNAME = ? WHERE ID = ?',(nickname,session["userID"],))
                cur.execute('UPDATE MEMINFO SET (MEM_NICKNAME, MEM_INTRO,MEM_YEAR,MEM_SEX,MEM_MAJ_1,MEM_MAJ_2) = (?,?,?,?,?,?) WHERE MEM_ID=?',((nickname, intro, year, sex, major1, major2, session["userID"],)))
                con.commit()
                flash('프로필 수정이 저장되었습니다! 확인해보세요!')
        except:
            con.rollback()
            flash('오류...다시 시도하세요:(')
        finally:
            return redirect(url_for("myprof"))
    return ''
    
@application.route("/friend_chat")
def friend_chat():
    user_id = session.get("userID")
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    
    cur.execute('''
    SELECT M.ID as friend_id, M.USERNAME, M.PROFILE_PIC, 
           (SELECT MESSAGE FROM MESSAGE 
            WHERE (SENDER_ID = ? AND RECIPIENT_ID = M.ID) OR (SENDER_ID = M.ID AND RECIPIENT_ID = ?)
            ORDER BY TIMESTAMP DESC LIMIT 1) as last_message,
           (SELECT TIMESTAMP FROM MESSAGE 
            WHERE (SENDER_ID = ? AND RECIPIENT_ID = M.ID) OR (SENDER_ID = M.ID AND RECIPIENT_ID = ?)
            ORDER BY TIMESTAMP DESC LIMIT 1) as last_timestamp
    FROM FRIEND F
    JOIN MEMBERS M ON (M.ID = F.USER1 OR M.ID = F.USER2)
    WHERE (F.USER1 = ? OR F.USER2 = ?) AND F.FRIEND_STATUS = 2 AND M.ID != ?
    ''', (user_id, user_id, user_id, user_id, user_id, user_id, user_id))
    
    friends = cur.fetchall()
    con.close()
    
    friend_list = [{
        'id': row['friend_id'],
        'name': row['USERNAME'],
        'profile_pic': row['PROFILE_PIC'],
        'last_message': row['last_message'],
        'last_timestamp': row['last_timestamp']
    } for row in friends]
    
    return render_template("friend_chat.html", friends=friend_list)

# 채팅 페이지로 이동하는 라우트
@application.route("/chat/<friend_id>")
def chat(friend_id):
    user_id = session.get("userID")
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    
    cur.execute('''
    SELECT MESSAGE, TIMESTAMP, SENDER_ID
    FROM MESSAGE
    WHERE (SENDER_ID = ? AND RECIPIENT_ID = ?) OR (SENDER_ID = ? AND RECIPIENT_ID = ?)
    ORDER BY TIMESTAMP ASC
    ''', (user_id, friend_id, friend_id, user_id))
    
    messages = cur.fetchall()
    con.close()
    
    chat_history = [{'message': row['MESSAGE'], 'timestamp': row['TIMESTAMP'], 'sender_id': row['SENDER_ID']} for row in messages]
    
    return render_template("chat.html", friend_id=friend_id, chat_history=chat_history)

@application.route("/start_matching")
def start_matching():
    print("Matching started")  # 로그 추가
    time.sleep(3)  # 3초 대기
    print("Matching completed")  # 로그 추가
    return jsonify(success=True)

# 메시지 저장 라우트
@application.route("/send_message", methods=["POST"])
def send_message():
    sender_id = session.get("userID")
    recipient_id = request.form["recipient_id"]
    message = request.form["message"]
    
    con = sql.connect('database.db')
    cur = con.cursor()
    
    cur.execute('INSERT INTO MESSAGE (SENDER_ID, RECIPIENT_ID, MESSAGE) VALUES (?, ?, ?)', 
                (sender_id, recipient_id, message))
    con.commit()
    con.close()
    
    return jsonify(success=True)

@application.route("/chat_history/<room>")
def chat_history(room):
    user_id = session.get("userID")
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    
    cur.execute('''
    SELECT MESSAGE, TIMESTAMP
    FROM MESSAGE
    WHERE (SENDER_ID = ? AND RECIPIENT_ID = ?) OR (SENDER_ID = ? AND RECIPIENT_ID = ?)
    ORDER BY TIMESTAMP ASC
    ''', (user_id, room, room, user_id))
    
    messages = cur.fetchall()
    con.close()
    
    chat_history = [{'message': row['MESSAGE'], 'timestamp': row['TIMESTAMP']} for row in messages]
    
    return jsonify(chat_history)

@application.route("/accept_friend_request", methods=["POST"])
def accept_friend_request():
    user_id = session.get("userID")
    sender_id = request.form["sender_id"]
    
    con = sql.connect('database.db')
    cur = con.cursor()
    
    try:
        # FRIEND 테이블에서 상태 업데이트
        cur.execute('UPDATE FRIEND SET FRIEND_STATUS = 2 WHERE (USER1 = ? AND USER2 = ?) OR (USER1 = ? AND USER2 = ?)', 
                    (user_id, sender_id, sender_id, user_id))
        
        # 수락한 사용자의 이름 가져오기
        cur.execute('SELECT USERNAME FROM MEMBERS WHERE ID = ?', (user_id,))
        username = cur.fetchone()[0]
        
        # NOTIFICATIONS 테이블에 알림 추가
        message = f"{username}님이 친구 요청을 수락하였습니다."
        cur.execute('INSERT INTO NOTIFICATIONS (USER_ID, SENDER_ID, MESSAGE) VALUES (?, ?, ?)',
                    (sender_id, user_id, message))
        
        con.commit()
        response = {"success": True}
    except Exception as e:
        con.rollback()
        response = {"success": False, "error": str(e)}
    finally:
        con.close()
    
    return jsonify(response)

@application.route("/accept_pending_friend_request", methods=["POST"])
def accept_pending_friend_request():
    user_id = session.get("userID")
    friend_id = request.form["friend_id"]
    
    con = sql.connect('database.db')
    cur = con.cursor()
    
    try:
        # FRIEND 테이블에서 상태 업데이트
        cur.execute('UPDATE FRIEND SET FRIEND_STATUS = 2 WHERE (USER1 = ? AND USER2 = ?) OR (USER1 = ? AND USER2 = ?)', 
                    (user_id, friend_id, friend_id, user_id))
        
        # 수락한 사용자의 이름 가져오기
        cur.execute('SELECT USERNAME FROM MEMBERS WHERE ID = ?', (user_id,))
        username = cur.fetchone()[0]
        
        # NOTIFICATIONS 테이블에 알림 추가
        message = f"{username}님이 친구 요청을 수락하였습니다."
        cur.execute('INSERT INTO NOTIFICATIONS (USER_ID, SENDER_ID, MESSAGE) VALUES (?, ?, ?)',
                    (friend_id, user_id, message))
        
        con.commit()
        response = {"success": True, "message": message}
    except Exception as e:
        con.rollback()
        response = {"success": False, "error": str(e)}
    finally:
        con.close()
    
    return jsonify(response)

@application.route("/notification_history")
def notification_history():
    user_id = session.get("userID")
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    
    # 알림 내역 조회
    cur.execute('''
    SELECT MESSAGE 
    FROM NOTIFICATIONS 
    WHERE USER_ID = ?
    ORDER BY ID DESC
    ''', (user_id,))
    notifications = cur.fetchall()
    con.close()

    notifications_list = [{'MESSAGE': row['MESSAGE']} for row in notifications]
    
    return render_template("notification_history.html", notifications=notifications_list)


if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0', port=5000,debug=True) #혜빈
#application.run(host ="0.0.0.0")

#if __name__ == "__main__":
#    application.run(host='0.0.0.0')