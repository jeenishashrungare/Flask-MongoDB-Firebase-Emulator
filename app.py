from flask import *
import json
from pymongo import MongoClient
# Connect to the MongoDB server
client = MongoClient('...') #Add your server address
db = client['Quizzard']
collection = db['data']
app = Flask(__name__)

# Retrieves and displays the question at an index
@app.route('/data/<int:index>', methods=['GET'])
def single_ques(index):
    question_document = collection.find_one()
    questions = question_document["Questions"]
    if(index<len(questions)):
        question = list(questions.keys())[index]
        return question
    else:
        return "Out of range!"

# Checks for the correctness of the answer
@app.route('/data/<int:index>/<path:answer>', methods=['GET'])
def check_ans(index,answer):

    question_document = collection.find_one()
    questions = question_document["Questions"]
    ans = list(questions.values())[index]
    answer=answer.strip()
    if(answer==ans):
        return "Correct Answer!"
    else:
        return "Wrong Answer!"

# Posts a new entry
@app.route('/data/', methods=['POST'])
def post_users():
    d = request.get_json()
    collection.update_one({},{"$set" : d})
    return "Added!"

# Put updates the entry; and creates a new one if it does not exist
@app.route('/data/', methods=['PUT'])
def put_users():
    request_params = request.get_json()
    updateObject = request_params
    result = collection.find_one_and_update({}, {"$set": updateObject}, upsert=True)
    return "Updation done"

# Patch checks if the entry already exists; and only then does it make the update 
@app.route('/data/', methods=['PATCH'])
def patch_users():
    request_params = request.get_json()
    question = list(request_params.keys())[0]
    answer = request_params[question]

    if collection.find_one({"Questions." + question: {"$exists": True}}) is None:
        return "Does not exist!"

    collection.update_one({}, {"$set": {f"{question}": answer}})
    return "Updation done!"

@app.route('/data/<int:index>', methods=['DELETE'])
def delete_entry_by_index(index):
  
    question_document = collection.find_one()
    questions = question_document["Questions"]

    if(index<len(questions)):
        question = str(list(questions.keys())[index])
        update_query = {'$unset': {'Questions.' + question: ''}}
        collection.update_one({'Questions': question_document["Questions"]}, update_query)
        return "Deleted!"
    else:
        return "Out of range!"


@app.route('/data.json', methods=['GET'])
def get_ques():

    if(not request.args.get('orderBy')):
        order_by="Questions"
    else:
        order_by = request.args.get('orderBy')
        order_by=order_by[1:-1]
    question_document = collection.find_one()
    questions = question_document[order_by]
    questions_list={}
    if(request.args.get('limitToFirst') or request.args.get('limit')):
        limit_to_first = int(request.args.get('limitToFirst')) if request.args.get('limitToFirst') else int(request.args.get('limit'))
        for i in range(0,limit_to_first):
          questions_list[list(questions.keys())[i]]=list(questions.values())[i]
    if(request.args.get('limitToLast')):
        limit_to_last = int(request.args.get('limitToLast'))
        total_questions = len(questions)
        start_index = total_questions - limit_to_last
        for i in range(start_index, total_questions):
            questions_list[list(questions.keys())[i]] = list(questions.values())[i]
    if(request.args.get('startAt') is not None and request.args.get('endAt') is not None):
        st = int(request.args.get('startAt'))
        e=int(request.args.get('endAt'))
        for i in range(st,e):
            questions_list[list(questions.keys())[i]] = list(questions.values())[i]
    elif(request.args.get('startAt')):
        st= int(request.args.get('startAt'))
        total_questions = len(questions)
        for i in range(st,total_questions):
            questions_list[list(questions.keys())[i]] = list(questions.values())[i]
    elif(request.args.get('endAt')):
        e= int(request.args.get('endAt'))
        for i in range(0,e):
            questions_list[list(questions.keys())[i]] = list(questions.values())[i]
    if(request.args.get('equalTo')):
        eq=request.args.get('equalTo')
        filtered_questions = {}
        for key, value in questions.items():
            if value == eq:
                filtered_questions[key] = value
        questions_list = filtered_questions

    questions_list = json.dumps(questions_list)
    return questions_list

if __name__ == '__main__':
    app.run(debug=True)
