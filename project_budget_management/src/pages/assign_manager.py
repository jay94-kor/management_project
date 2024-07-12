import streamlit as st
from src.components.db import get_db_connection
from src.components.common import select_project

def show():
    st.title("담당자 지정")

    project_id, project_name = select_project()
    if not project_id:
        return

    try:
        conn = get_db_connection()
        c = conn.cursor()

        # 사용자 선택
        users = c.execute('SELECT id, username FROM users').fetchall()
        if not users:
            st.warning("사용자가 없습니다. 먼저 사용자를 추가해주세요.")
            return

        user_options = {user[1]: user[0] for user in users}
        manager_name = st.selectbox('담당자 선택', list(user_options.keys()))
        manager_id = user_options[manager_name]

        if st.button('담당자 지정'):
            c.execute('UPDATE projects SET created_by = ? WHERE id = ?', (manager_id, project_id))
            conn.commit()
            st.success(f'{manager_name}님이 {project_name} 프로젝트의 담당자로 지정되었습니다.')

    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
    finally:
        if conn:
            conn.close()