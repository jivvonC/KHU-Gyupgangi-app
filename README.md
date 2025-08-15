# 겹강이 (Gyeopgang-i)

## 📌 프로젝트 소개
**겹강이**는 대학생들이 같은 강의를 듣는 친구를 쉽게 찾을 수 있도록 도와주는 웹·모바일 서비스입니다.  
이용자가 자신의 시간표를 등록하면, 시스템이 다른 이용자들의 시간표와 비교하여 **겹치는 강의가 있는 친구**를 매칭해줍니다.  
이를 통해 조별 과제 팀원 모집, 수업 정보 공유, 함께 공부할 친구 찾기 등 대학 생활 전반에서 교류를 촉진합니다.


## ⏳ 개발 기간
**2024.03 – 2024.06**


## 👥 멤버 구성
| 이름 | 역할 | 주요 담당 |
|------|------|-----------|
| 전지원 | 프론트엔드 개발 & DB 설계 | HTML/CSS UI 디자인, SQLite3 DB 설계 및 연동 |
| 권혜빈 | 백엔드 개발 | Flask 서버 구축, 시간표 등록 및 조회 로직 구현, 채팅 서비스 구현 |
| 곽가영 | 백엔드 개발 | Flask 서버 구축, 매칭 로직 구현, PythonAnywhere 배포 및 호스팅 |


## 💻 개발 환경
- **Front End:** HTML, CSS  
- **Back End:** Python (Flask)  
- **Database:** SQLite3  
- **Design Pattern:** MVC  
- **Hosting:** PythonAnywhere  
- **Mobile App:** React Native (Web-View)  
- **OS:** Windows  


## ✨ 주요 기능
- **회원 가입**
  - ID/PW 설정 및 중복 방지
  - 프로필 등록 (학번, 성별, 자기소개)
- **시간표 관리**
  - 강의 검색 및 시간표 추가
  - 종합 강의 시간표 조회
- **친구 매칭**
  - 최소·최대 겹강 개수 조건 설정
  - 같은 강의를 듣는 친구 리스트 제공
- **소셜 기능**
  - 친구 신청 및 수락
  - 채팅 기능 지원 (친구 수락 후 개인정보 확인 가능)


## 📈 기대 효과
- 대학 생활에서 새로운 친구를 쉽게 찾을 수 있음
- 팀 과제, 시험 대비, 학습 모임 등 교우관계 및 학업 성취도 향상
- 내향적인 학생, 복학생, 다전공생 등도 쉽게 교류 가능


## 🖥️ 시스템 구성
- **웹 버전:** Flask + SQLite3 + HTML/CSS
- **모바일 앱:** React Native Web-View
- **호스팅:** PythonAnywhere


## 🚀 실행 방법
### 로컬 실행
```bash
# 1. 저장소 클론
git clone https://github.com/username/gyeopgang-i.git

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 실행
flask run
```
