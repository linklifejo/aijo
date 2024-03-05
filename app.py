import streamlit as st
import openapi
import streamlit.components.v1 as components
import random
from database import removeDbFile,setupTables, insertData, updateData, deleteData, queryByField, queryToDataframe, queryJoin
db_name = 'inet.db'

def main():
    if 'select_id' not in st.session_state:
        st.session_state.select_id = 0
    st.title("Database Management")
    # 데이터베이스 테이블 설정
    if st.button("Setup Database Tables"):
        removeDbFile(db_name)
        setupTables()
        st.success("Database tables set up successfully.")

    operation = st.selectbox("Choose Operation", ["Insert", "Update", "Delete", "Select", "Join"])
    if operation == "Insert":
        table = st.selectbox("Choose Table", ["employees", "customers", "members", "apikeys", "assistants", "threads","files","realations"])
        with st.form(key='insert_form'):
            # 각 테이블에 따른 입력 필드 추가
            if table == "employees":
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email_address = st.text_input("Email Address")
                phone_number = st.text_input("Phone Number")
                department = st.text_input("Department")
                position = st.text_input("Position")
                hire_date = st.date_input("Hire Date")
                salary = st.number_input("Salary", format="%d")
                employment_status = st.selectbox("Employment Status", ["Full-time", "Part-time", "Contract", "Intern"])
                date_of_birth = st.date_input("Date of Birth")
                address = st.text_input("Address")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                nationality = st.text_input("Nationality")
                emergency_contact_name = st.text_input("Emergency Contact Name")
                emergency_contact_relationship = st.text_input("Emergency Contact Relationship")
                emergency_contact_number = st.text_input("Emergency Contact Number")
                description = st.text_area("Description")
                data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email_address": email_address,
                    "phone_number": phone_number,
                    "department": department,
                    "position": position,
                    "hire_date": str(hire_date),
                    "salary": salary,
                    "employment_status": employment_status,
                    "date_of_birth": str(date_of_birth),
                    "address": address,
                    "gender": gender,
                    "nationality": nationality,
                    "emergency_contact_name": emergency_contact_name,
                    "emergency_contact_relationship": emergency_contact_relationship,
                    "emergency_contact_number": emergency_contact_number,
                    "description": description
                }
                submit_button = st.form_submit_button(label='Insert Data')
                if submit_button:
                    insertData(table, data,unique_key_column="email_address")
                    st.success("Data inserted successfully!")
            elif table == "customers":
                st.write('customer')
                customer_id = st.text_input("Customer ID")
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email_address = st.text_input("Email Address")
                phone_number = st.text_input("Phone Number")
                address = st.text_input("Address")
                city = st.text_input("City")
                state_province = st.text_input("State/Province")
                postal_code = st.text_input("Postal Code")
                country = st.text_input("Country")
                date_of_birth = st.date_input("Date of Birth")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                account_creation_date = st.date_input("Account Creation Date")
                last_purchase_date = st.date_input("Last Purchase Date")
                customer_segment = st.text_input("Customer Segment")
                preferences = st.text_input("Preferences")
                loyalty_points = st.number_input("Loyalty Points", min_value=0, step=1)
                description = st.text_area("Description")
            
                submit_button = st.form_submit_button(label='Insert Customer')
                if submit_button:
                    data = {
                        "customer_id": customer_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email_address": email_address,
                        "phone_number": phone_number,
                        "address": address,
                        "city": city,
                        "state_province": state_province,
                        "postal_code": postal_code,
                        "country": country,
                        "date_of_birth": str(date_of_birth),
                        "gender": gender,
                        "account_creation_date": str(account_creation_date),
                        "last_purchase_date": str(last_purchase_date),
                        "customer_segment": customer_segment,
                        "preferences": preferences,
                        "loyalty_points": loyalty_points,
                        "description": description
                    }
                    insertData("customers", data,unique_key_column="email_address")
                    st.success("Customer data inserted successfully!")
            elif table == "members":
                    member_id = st.text_input("Member ID")
                    name = st.text_input("Name")
                    password = st.text_input("Password", type="password")
                    first_name = st.text_input("First Name")
                    last_name = st.text_input("Last Name")
                    email_address = st.text_input("Email Address")
                    phone_number = st.text_input("Phone Number")
                    address = st.text_input("Address")
                    date_of_birth = st.date_input("Date of Birth")
                    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                    registration_date = st.date_input("Registration Date")
                    membership_type = st.text_input("Membership Type")
                    membership_status = st.selectbox("Membership Status", ["Active", "Inactive"])
                    last_login_date = st.date_input("Last Login Date")
                    profile_photo = st.file_uploader("Upload Profile Photo", type=["jpg", "png", "jpeg"])
                    preferences = st.text_input("Preferences")
                    notes = st.text_area("Notes")
                    description = st.text_area("Description")

                    submit_button = st.form_submit_button(label='Insert Member')
                    if submit_button:
                        data = {
                            "member_id": member_id,
                            "name": name,
                            "password": password,
                            "first_name": first_name,
                            "last_name": last_name,
                            "email_address": email_address,
                            "phone_number": phone_number,
                            "address": address,
                            "date_of_birth": str(date_of_birth),
                            "gender": gender,
                            "registration_date": str(registration_date),
                            "membership_type": membership_type,
                            "membership_status": membership_status,
                            "last_login_date": str(last_login_date),
                            "profile_photo": profile_photo,
                            "preferences": preferences,
                            "notes": notes,
                            "description": description
                        }
                        insertData("members", data,unique_key_column="email_address")
                        st.success("Member data inserted successfully!")
            elif table == "apikeys":
                api_key_value = st.text_input("API Key Value")
                member_id = st.number_input("member ID", min_value=1)
                status = st.selectbox("Status", ["Active", "Inactive", "Revoked"])
                description = st.text_area("Description/Notes",value="회원관리자")
                submit_button = st.form_submit_button(label='Insert API Key')
                if submit_button:
                    data = {
                        "api_key_value": api_key_value,
                        "member_id": member_id,
                        "status": status,
                        "description": description
                    }
                    insertData("apikeys", data, unique_key_column="api_key_value")
                    st.success("API Key data inserted successfully!")
            elif table == "assistants":
                assistant_id = st.text_input("Assistant ID")
                instruction = st.text_area("Instruction",value="채팅")
                query = f'SELECT * FROM {'apikeys'}'
                # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
                query_data = queryToDataframe(query)
                # 데이터가 없는 경우를 확인합니다.
                if len(query_data) > 0:
                    options = ["Select..."] + [f"{row['id']} - {row['description']}" for index, row in query_data.iterrows()]
                    selected = st.selectbox("api-key", options=options)
                    if selected != "Select...":
                        st.session_state.selected_id = int(selected.split(" - ")[0])
                        row = query_data[query_data['id'] == st.session_state.selected_id].iloc[0]               
                model = st.text_input("Model")
                code_interpreter = st.toggle("code interpreter",value=False)
                retrieval = st.toggle("retrieval",value=False)
                options = st.multiselect(
                            'functions select',
                            ['망고', '오렌지', '사과', '바나나'],
                            ['망고', '오렌지'])
                file_ids = st.file_uploader("파일선택(다중가능)(csv or excel)", type=['csv', 'xls', 'xlsx'],accept_multiple_files=True )
                x=set()
                if file_ids is not None:
                    for i in file_ids:
                        x.add(i.name)
                    
                    for j in list(x):
                        st.write(j)
                status = st.text_input("Status")
                creation_date = st.text_input("Creation Date")
                member_id = st.number_input("member_id")
                description = st.text_area("Description")
                apikey_id = st.text_input("apikey_id")

                submit_button = st.form_submit_button(label='Insert Assistant')
                if submit_button:
                    data = {
                        "assistant_id": assistant_id,
                        "instruction": instruction,
                        "model": model,
                        "code_interpreter": code_interpreter,
                        "retrieval": retrieval,
                        "funcitons": functions,
                        "file_ids": file_ids,
                        "status": status,
                        "creation_date": creation_date,
                        "member_id": member_id,
                        "description": description,
                        "apikey_id": st.session_state.selected_id
                    }
                    insertData(table, data, unique_key_column="assistant_id")
                    st.success("Assistant data inserted successfully!")
            elif table == "threads":
                thread_id = st.text_input("Thread ID")
                query = f'SELECT * FROM {'assistants'}'
                # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
                query_data = queryToDataframe(query)
                # 데이터가 없는 경우를 확인합니다.
                if len(query_data) > 0:
                    options = ["Select..."] + [f"{row['id']} - {row['description']}" for index, row in query_data.iterrows()]
                    selected = st.selectbox("api-key", options=options)
                    if selected != "Select...":
                        st.session_state.selected_id = int(selected.split(" - ")[0])
                        row = query_data[query_data['id'] == st.session_state.selected_id].iloc[0]  
                created_date = st.date_input("Created Date")
                member_id = st.number_input("member_id")
                status = st.selectbox("Status", ["Active", "Inactive"])
                description = st.text_area("Description")

                submit_button = st.form_submit_button(label='Insert Thread')
                if submit_button:
                    data = {
                        "thread_id": thread_id,
                        "assistant_id": st.session_state.selected_id,
                        "created_date": str(created_date),
                        "member_id": member_id,
                        "status": status,
                        "description": description
                    }
                    insertData("threads", data, unique_key_column="thread_id")
                    st.success("Thread data inserted successfully!")
            elif table == "files":
                file_id = st.text_input("File ID")
                query = f'SELECT * FROM {'assistants'}'
                # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
                query_data = queryToDataframe(query)
                # 데이터가 없는 경우를 확인합니다.
                if len(query_data) > 0:
                    options = ["Select..."] + [f"{row['id']} - {row['description']}" for index, row in query_data.iterrows()]
                    selected = st.selectbox("api-key", options=options)
                    if selected != "Select...":
                        st.session_state.selected_id = int(selected.split(" - ")[0])
                        row = query_data[query_data['id'] == st.session_state.selected_id].iloc[0]  
                name = st.text_input("File Name")
                created_date = st.date_input("Created Date")
                used = st.text_input("File Used")
                status = st.selectbox("Status", ["Active", "Inactive"])
                member_id = st.number_input("member_id")
                description = st.text_area("Description")
                submit_button = st.form_submit_button(label='Insert Thread')
                if submit_button:
                    data = {
                        "file_id": file_id,
                        "assistant_id": st.session_state.selected_id,
                        "created_date": str(created_date),
                        "used": used,
                        "status": status,
                        "member_id": member_id,
                        "description": description
                    }
                    insertData("files", data, unique_key_column="file_id")
                    st.success("File data inserted successfully!")
            elif table == "relations":
                member_id = st.text_input("Member ID")
                name = st.text_input("File Name")
                assistant_id = st.text_input("Assistant ID")
                thread_id = st.text_input("Thread ID")
                apikey_id = st.text_input("Apikey ID")
                status = st.selectbox("Status", ["Active", "Inactive"])
                description = st.text_area("Description")
                submit_button = st.form_submit_button(label='Insert Thread')
                if submit_button:
                    data = {
                        "member_id": int(member_id),
                        "assistant_id": assistant_id,
                        "thread_id": thread_id,
                        "apikey_id": apikey_id,
                        "status": status,
                        "description": description
                    }
                    insertData("relations", data, unique_key_column="id")
                    st.success("Relation data inserted successfully!")                    
    elif operation == "Update":
        data = {} # 수정할 데이터를 저장할 딕셔너리
        st.session_state.selected_id = 0
        table = st.selectbox("Choose Table", ["employees", "customers", "members", "apikeys", "assistants", "threads","files","relations"])
        with st.form(key='update_form'):
            query = f'SELECT * FROM {table}'
            # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
            query_data = queryToDataframe(query)
            # 데이터가 없는 경우를 확인합니다.
            if len(query_data) > 0:
                options = ["Select..."] + [f"{row['id']} - {row['description']}" for index, row in query_data.iterrows()]
                selected = st.selectbox("선택", options=options)
                if selected != "Select...":
                    st.session_state.selected_id = int(selected.split(" - ")[0])
                    row = query_data[query_data['id'] == st.session_state.selected_id].iloc[0]
                # 사용자 입력을 기반으로 data 딕셔너리를 채움
                for column in query_data.columns:
                    if column == 'id':
                        st.session_state.uid = query_data[column].values[0]  # 조건값으로 사용할 id 값 저장
                    else:
                        # Streamlit의 입력 필드로부터 값을 받아 data 딕셔너리에 저장
                        data[column] = st.text_input(column, value=query_data[column].values[0])
                    

            submit_button = st.form_submit_button(label='Update Data')
            if submit_button:
                if len(data) > 0:
                    updateData(table, data, "id", st.session_state.selected_id)
                    st.success("Data updated successfully!")
                else:
                    st.write('수정할 데이타가 없습니다.')
    elif operation == "Delete":
        table = st.selectbox("Choose Table", ["employees", "customers", "members", "apikeys", "assistants", "threads","files","relations"])
        with st.form(key='delete_form'):
            query = f'SELECT * FROM {table}'
            # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
            query_data = queryToDataframe(query)
            # 데이터가 없는 경우를 확인합니다.
            if len(query_data) > 0:
                options = ["Select..."] + [f"{row['id']} - {row['description']}" for index, row in query_data.iterrows()]
                selected = st.selectbox("선택", options=options)
                if selected != "Select...":
                    st.session_state.selected_id = int(selected.split(" - ")[0])
            submit_button = st.form_submit_button(label='Delete Data')
            if submit_button:
                deleteData(table, "id", st.session_state.selected_id)
                st.success("Data deleted successfully!")

    elif operation == "Select":
        table = st.selectbox("Choose Table to View", ["employees", "customers", "members", "apikeys", "assistants", "threads","files","relations"])
        with st.form(key='select_form'):
            submit_button = st.form_submit_button(label='View Data')
            if submit_button:
                df = queryToDataframe(f"SELECT * FROM {table}")
                
                if len(df) > 0:
                    st.dataframe(df)
                    st.write('레코드 갯수 : ',len(df))

    elif operation == "Join":
        with st.form(key='join_form'):
            table1 = st.selectbox("Choose First Table", ["employees", "customers", "members", "apikeys", "assistants", "threads"])
            table2 = st.selectbox("Choose Second Table", ["employees", "customers", "members", "apikeys", "assistants", "threads"])
            query = f'SELECT * FROM {table}'
            # queryToDataframe 함수를 사용하여 데이터를 가져옵니다.
            query_data = queryToDataframe(query)
            # 데이터가 없는 경우를 확인합니다.
            if len(query_data) > 0:
                options = ["Select..."] + [f"{row['id']} - {row['description']}" for index, row in query_data.iterrows()]
                selected = st.selectbox("선택", options=options)
                if selected != "Select...":
                    st.session_state.selected_id = int(selected.split(" - ")[0])
            join_condition = st.text_input("Join Condition (e.g., employees.id = customers.assigned_employee_id)")
            submit_button = st.form_submit_button(label='Join Data')
            if submit_button:
                df = queryJoin(table1, table2, join_condition, "id", st.session_state.selected_id)
                st.dataframe(df)

if __name__ == "__main__":
    main()





