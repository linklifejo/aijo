from openai import OpenAI
import time
import json
from database import removeDbFile,setupTables, insertData, updateData, deleteData, queryByField, queryToDataframe, queryJoin
import logging
import os
def isrelations(client,apikey_id,member_id=1):
    query_data = queryByField("relations","member_id",member_id)
    if query_data is not None:

        if len(query_data) > 0:
            for index,row in query_data.iterrows():
                assistant_id = row['assistant_id']
                thread_id = row['thread_id']
                return assistant_id, thread_id
        else:
            assistant_id =assistant_create(client)
            thread_id =thread_create(client)
            insertData('relations', {
            'member_id': member_id,
            'assistant_id': assistant_id,  
            'thread_id': thread_id,  
            'apikey_id': apikey_id  
            },"id")
            return assistant_id, thread_id
# api_key = os.environ.get("OPENAI_API_KEY")
# 업로드할 파일들의 경로를 지정합니다.
# files_to_upload = [
#     "data/language_models_are_unsupervised_multitask_learners.pdf",
#     "data/SPRI_AI_Brief_2023년12월호.pdf",
# ]

# 파일을 업로드합니다.
# file_ids = upload_files(files_to_upload)
# 업로드한 모든 파일 ID 와 파일명을 출력합니다.
# for file in client.files.list():
#     print(f"[파일 ID] {file.id} [파일명] {file.filename}")

# tools = [
#     {
#         "type":"function",
#         "function": {
#             "name":"oil_price",
#             "description":"Get current oil prices - Dubai, WTI, and Brent",
#             "parameters": {
#                 "type":"object",
#                 "properties": {}
#             },
#             "required": []
#         }
#     },
#     {
#         "type":"function",
#         "function": {
#             "name":"usd_krw",
#             "description":"Get current exchange rate from USD to KRW",
#             "parameters": {
#                 "type":"object",
#                 "properties": {}
#             },
#             "required": []
#         }
#     }
# ]


# 스키마를 정의합니다.
# function_schema = {
#     "name": "generate_quiz",
#     "description": "Generate a quiz to the student, and returns the student's response. A single quiz has multiple questions.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "title": {"type": "string"},
#             "questions": {
#                 "type": "array",
#                 "description": "An array of questions, each with a title and multiple choice options.",
#                 "items": {
#                     "type": "object",
#                                         "properties": {
#                         "question_text": {"type": "string"},
#                         "choices": {"type": "array", "items": {"type": "string"}},
#                     },
#                     "required": ["question_text", "choices"],
#                 },
#             },
#         },
#         "required": ["title", "questions"],
#     },
# }


# Logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def show_json(obj):
    # obj 객체가 가지고 있는 model_dump_json 메소드를 호출하여 JSON 문자열을 얻습니다.
    try:
        # obj의 model_dump_json() 메소드로부터 반환된 JSON 문자열을 Python 딕셔너리로 변환합니다.
        obj_dict = json.loads(obj.model_dump_json())
        
        # 딕셔너리를 이쁘게 포맷된 JSON 문자열로 출력합니다.
        # Jupyter notebook이나 유사한 환경에서는:
        # display(obj_dict)
        
        # 표준 Python 환경에서는 print 사용
        # print(json.dumps(obj_dict, indent=4))
        
        # JSON 데이터에서 'Assistant ID'를 추출하여 출력합니다.
        # 'assistant_id' 키가 없는 경우 'Assistant ID not found'를 출력합니다.
        id = obj_dict.get("id", "Assistant ID를 찾을 수 없습니다.")
        return id        
    except json.JSONDecodeError as e:
        print("JSON 데이터를 디코딩하는 중 오류가 발생했습니다:", e)
    except AttributeError as e:
        print("해당 객체에 'model_dump_json' 메소드가 없습니다:", e)

def login(id, ps):
    sql = "SELECT * FROM members WHERE member_id = ? and password = ?"
    df = queryToDataframe(sql,(id,ps))
    if len(df) > 0:
        return True
    return False

def client_connect(openai_api_key):
    try:
        client = OpenAI(api_key=openai_api_key)
        return client
    except Exception as e:
        return False
def load_api_key():
    sql = "SELECT * FROM apikeys WHERE status = 'Active'"
    df = queryToDataframe(sql)
    if len(df) > 0:
        for index, row in df.iterrows():
            return row['api_key_value']
    else:
        return None
def file_create(client, file, use='assistants'):
    file = client.files.create(
    file=open(file, "rb"),
    purpose=use
    )
    return file.id
def file_upload(client, files):
    uploaded_files = []
    for filepath in files:
        file = client.files.create(
            file=open(
                # 업로드할 파일의 경로를 지정합니다.
                filepath,  # 파일경로. (예시) data/sample.pdf
                "rb",
            ),
            purpose="assistants",
        )
        uploaded_files.append(file.id)
        # print(f"[업로드한 파일 ID]\n{file.id}")
    return uploaded_files
def file_retrieve(client, file_id):
    return client.files.retrieve(file_id)

def file_delete(client, file_id):
    client.files.delete(file_id)

def file_list(client):
    return client.files.list()    

def assistants_delete(client): #여러개의 어시스턴트들을 일괄삭제
    my_assistants = assistant_list(client)

    i=0
    while True:
        try:
            print(assistant_delete(client, show_json(my_assistants.data[i])))
            time.sleep(1)
            # print(show_json(my_assistants.data[i]))
        except Exception as e:
            break
        i+=1
    return f"어시스턴트 {str(i)}를 삭제하였습니다."
# def assistant_create(client, name="chat bot", model="gpt-4-turbo-preview"):
#     assistant = client.beta.assistants.create(
#         name=name,
#         model=model,
#     )
#     return assistant.id

def assistant_create(client,name="chat bot",model="gpt-4-turbo-preview"):
    assistant = client.beta.assistants.create(
        name=name,
        # instructions="You are an expert in generating multiple choice quizzes. Create quizzes based on uploaded files.",
        model=model,
        # model="gpt-3.5-turbo-1106",
        tools=[
            {"type": "code_interpreter"},
            {"type": "retrieval"},
        ]
    )
    return assistant.id
# def assistant_create(function_schema,file_ids,client):
#     assistant = client.beta.assistants.create(
#         name="Quiz Generator",
#         instructions="You are an expert in generating multiple choice quizzes. Create quizzes based on uploaded files.",
#         # model="gpt-4-turbo-preview",
#         model="gpt-3.5-turbo-1106",
#         tools=[
#             {"type": "interpreter"},
#             {"type": "retrieval"},
#             {"type": "function", "function": function_schema},
#         ],
#         file_ids=file_ids,
#     )
#     return assistant.id
def assistant_update(client, assistant_id,file_ids):
    assistant = client.beta.assistants.update(
        assistant_id,
        # retrieval 도구를 추가합니다.
        tools=[
            {"type": "code_interpreter"},
            {"type": "retrieval"},
        ],
        file_ids=file_ids,  # 업로드한 파일 ID를 지정합니다.
        # Assistant 의 역할을 설명합니다.
        instructions="You are a expert in Document Retrieval. Answer questions using the uploaded documents.",
    )
    return assistant.id
    
def assistant_delete(client, assistant_id):
    response = client.beta.assistants.delete(assistant_id)
    return response
def assistant_list(client):
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit="20",
    )

    return my_assistants
def thread_create(client):    
    thread = client.beta.threads.create()
    return thread.id
def thread_delete(client, thread_id):
    response = client.beta.threads.delete(thread_id)

def thread_retrieve(client, thread_id):    
    my_thread = client.beta.threads.retrieve(thread_id)

def run_create(client, assistant_id, thread_id):
    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id
    )   
    return run.id

def ask(client, assistant_id, thread_id, user_message):
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_message
    )
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    run = wait_on_run(client, run, thread_id)
    return run

def wait_on_run(client, run, thread_id):
    while run.status == "queued" or run.status == "in_progress":
        # 3-3. 실행 상태를 최신 정보로 업데이트합니다.
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(2)
    return run

def result(client, run, thread_id):
    while True:
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id)
            msg = messages.data[0].content[0].text.value
            return msg
                # for msg in reversed(thread_messages.data):
                #     print(type(msg.content[0].text.value))   
                #     # print(f"{msg.role}: {msg.content[0].text.value}") 
                #     # print(msg.content[0].text.value)
                # break
        elif run.status == 'requires_action':
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool in tool_calls:
                func_name = tool.function.name
                kwargs = json.loads(tool.function.arguments)
                # responses = display_quiz(arguments["title"], arguments["questions"])
                output = globals()[func_name](**kwargs)
                # output = locals()[func_name](**kwargs)
                tool_outputs.append(
                    {
                        "tool_call_id":tool.id,
                        "output":str(output)
                    }
                )
            run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
            )
            run = wait_on_run(client,run,thread_id)



