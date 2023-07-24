from flask import Flask,request,Response
import pymongo
import json


app=Flask(__name__)

try:
    mongo=pymongo.MongoClient(host='localhost',port=27017,serverSelectionTimeoutMS=10000)
    db=mongo.sample

    mongo.server_info()
except:
    print("FAILED TO ESTABLISH CONNECTION")





#----------------------------------------------------------------------->UNIQUE IDs
def get_id():
    
    #retrieving all IDs
    l=db.tasks.find({},{"_id":False})
    l=list(l)
    avlbl_ids=[]
    for i in l:
        avlbl_ids.append(int(i["id"]))  

    #if no IDs return 1
    avlbl_ids.sort()
    if len(avlbl_ids)==0:               
        return 1
    
    #create new ID
    return avlbl_ids[-1]+1              

    



#------------------------------------------------------------------------>TASK 1 & 6(EXTRA CREDITS)
@app.route('/v1/tasks',methods=["POST"])
def create_tasks():
    
    d=request.get_json()

    """#   TASK 1 : CREATE A NEW TASK
    #if JSON recieved is for single task,
    the try block is executed"""


    """#   TASK 6 : (EXTRA CREDITS) BULK ADD TASKS
    passing JSON for multiple tasks has key "tasks",
    the JSON for single task doesn't,and accessing it produces a KeyError"""
    try:
        id=get_id()
        db.avlbl_ids.delete_one({"id":int(id)})
        d={"id":id,"title":d["title"],"is_completed":d.get("is_completed","false")}
        db.tasks.insert_one(d)
        return Response(response=json.dumps({'id' : id}),status=201,mimetype='application/json')
    


    except KeyError:
        d=d["tasks"]
        l=[]
        for i in d:
            temp=i
            temp["id"]=get_id()
            temp["title"]=i["title"]
            temp.setdefault("is_completed","false")
            l.append(temp)
            db.tasks.insert_one(temp)

        k=[]
        for i in l:
            k.append({'id':i["id"]})
        
        return Response(response=json.dumps({'tasks':k},indent=4),status=201,mimetype='application/json')








#------------------------------------------------------------------------------>TASK 2
@app.route('/v1/tasks',methods=["GET"])
def list_all_tasks():

    #   TASK 2 : LIST ALL TASKS CREATED
    d=db.tasks.find({},{"_id":False})
    d=list(d)
    return Response(response=json.dumps({"tasks":d},indent=4),status=200,mimetype='application/json')






#------------------------------------------------------------------------------>TASK 3
@app.route('/v1/tasks/<id>',methods=["GET"])
def list_one_task(id):

    #   TASK 3 : GET A SPECIFIC TASK
    d=db.tasks.find({"id":int(id)},{"_id":False})
    d=list(d)
    try:
        print(d)
        return Response(response=json.dumps(d[0]),status=200,mimetype='application/json')
    except:
        return Response(response=json.dumps({"error":"There is no task at that id"}),status=404,mimetype='application/json')



#------------------------------------------------------------------------------>TASK 4
@app.route('/v1/tasks/<id>',methods=["DELETE"])
def delete_one_task(id):

    #   TASK 4 : DELETE A SPECIFIC TASK
    try:
        b=db.tasks.find({"id":int(id)})
        if b==None:
            raise()
        db.tasks.delete_one({"id":int(id)})
        db.avlbl_ids.insert_one({"id":int(id)})
        return id
    except:
        return Response(response="None",status=204,mimetype="text/plain")






#------------------------------------------------------------------------------>TASK 5
@app.route('/v1/tasks/<id>',methods=["PUT"])
def edit_one_task(id):
    

    #   TASK 5 : EDIT THE TITLE OR COMPLETION OF A SPECIFIC TASK
    d=request.get_json()
    try:
        temp=db.tasks.find({"id":int(id)},{"_id":False})
        
        temp=list(temp)[0]
        for i in d:
            temp[i]=d[i]

        print({"title": temp["title"],"is_completed":temp["is_completed"]})
        db.tasks.update_one({"id":int(id)},{"$set":{"title": temp["title"],"is_completed":temp["is_completed"]}})
        return Response(response="None",status=204)
    except:
        return Response(response=json.dumps({"error":"There is no task at that id"}),status=404,mimetype="application/json")







#------------------------------------------------------------------------------>TASK 7(EXTRA CREDITS)
@app.route('/v1/tasks',methods=["DELETE"])
def delete_multiple_tasks():

    #   TASK 7 : (EXTRA CREDITS) BULK DELETE TASKS
    l=request.get_json()
    l=l["tasks"]
    print(l)
    for i in l:
        db.tasks.delete_one({"id":int(i["id"])})
        db.avlbl_ids.insert_one({"id":int(i["id"])})
    return Response(response="None",status=204)

if __name__=='__main__':
    app.run(port=8080,debug=True)