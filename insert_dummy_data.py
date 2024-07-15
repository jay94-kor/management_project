import sqlite3
from datetime import date, datetime

def insert_dummy_data():
    conn = sqlite3.connect('project_management.db')
    cursor = conn.cursor()

    # 프로젝트 더미 데이터
    projects = [
        ('P001', '웹사이트 리뉴얼', '에이비씨 주식회사', '김철수', 'IT 개발팀', 100000000, 20000000),
        ('P002', '모바일 앱 개발', '엑스와이지 기업', '박영희', '모바일 개발팀', 80000000, 15000000),
        ('P003', '데이터 분석 시스템', '123 주식회사', '이민수', '데이터 사이언스팀', 150000000, 30000000)
    ]

    cursor.executemany('''
    INSERT INTO Project (project_code, name, client, pm, department, contract_amount, expected_profit)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', projects)

    # 프로젝트 아이템 더미 데이터
    project_items = [
        (1, 'P001', '개발', '프론트엔드 개발', 'React를 이용한 웹 프론트엔드 개발', 1, '식', None, None, 30000000, 30000000, 30000000),
        (1, 'P001', '개발', '백엔드 개발', 'Django를 이용한 백엔드 API 개발', 1, '식', None, None, 40000000, 40000000, 40000000),
        (2, 'P002', '개발', 'iOS 앱 개발', 'Swift를 이용한 iOS 앱 개발', 1, '식', None, None, 35000000, 35000000, 35000000),
        (2, 'P002', '개발', 'Android 앱 개발', 'Kotlin을 이용한 Android 앱 개발', 1, '식', None, None, 35000000, 35000000, 35000000),
        (3, 'P003', '개발', '데이터 파이프라인 구축', 'Apache Airflow를 이용한 데이터 파이프라인 구축', 1, '식', None, None, 50000000, 50000000, 50000000),
        (3, 'P003', '개발', '대시보드 개발', 'Tableau를 이용한 데이터 시각화 대시보드 개발', 1, '식', None, None, 40000000, 40000000, 40000000)
    ]

    cursor.executemany('''
    INSERT INTO ProjectItem (project_id, project_code, category, item, description, quantity1, spec1, quantity2, spec2, unit_price, total_price, assigned_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', project_items)

    # 지출 요청 더미 데이터
    expenditure_requests = [
        (1, 'P001', 10000000, '인건비', '프론트엔드 개발자 1개월 인건비', date(2023, 6, 1), None, None),
        (2, 'P002', 5000000, '외주비', 'UI/UX 디자인 외주 비용', date(2023, 6, 15), None, None),
        (3, 'P003', 20000000, '재료비', '서버 장비 구매', date(2023, 7, 1), None, None)
    ]

    cursor.executemany('''
    INSERT INTO ExpenditureRequest (project_id, project_code, amount, expenditure_type, reason, planned_date, file_name, file_contents)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', expenditure_requests)

    conn.commit()
    conn.close()

    print("더미 데이터가 성공적으로 삽입되었습니다.")

if __name__ == "__main__":
    insert_dummy_data()