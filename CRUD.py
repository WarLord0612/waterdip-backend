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

    

@app.route('/v1/tasks',methods=["POST"])
def create_tasks():
    
    d=request.get_json()
    print(d)
    try:
        id=db.tasks.count_documents({})
        d={"id":id,"title":d["title"],"is_completed":d.get("is_completed","false")}
        db.tasks.insert_one(d)
        return Response(response=json.dumps({'id' : id}),status=201,mimetype='application/json')
    except KeyError:
        d=d["tasks"]
        c=db.tasks.count_documents({})+1
        k=c
        for i in d:
            temp=i
            temp["id"]=c
            c+=1
            temp.setdefault("is_completed","false")

        db.tasks.insert_many(d)
        l=[]
        for i in d:
            l.append({'id':k})
            k+=1

        print(l)
        return Response(response=json.dumps({'tasks':l},indent=4),status=201,mimetype='application/json')


@app.route('/v1/tasks',methods=["GET"])
def list_all_tasks():

    d=db.tasks.find({},{"_id":False})
    d=list(d)
    return Response(response=json.dumps({"tasks":d},indent=4),status=200,mimetype='application/json')


@app.route('/v1/tasks/<id>',methods=["GET"])
def list_one_task(id):

    d=db.tasks.find({"id":int(id)},{"_id":False})
    d=list(d)
    try:
        print(d)
        return Response(response=json.dumps(d[0]),status=200,mimetype='application/json')
    except:
        return Response(response=json.dumps({"error":"There is no task at that id"}),status=404,mimetype='application/json')
        
@app.route('/v1/tasks/<id>',methods=["DELETE"])
def delete_one_task(id):
    try:
        b=db.tasks.find_one({"id":id})
        if b==None:
            raise()
        db.tasks.delete_one({"id":int(id)})
        return id
    except:
        return Response(response="None",status=204,mimetype="text/plain")

@app.route('/v1/tasks/<id>',methods=["PUT"])
def edit_one_task(id):
    

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


@app.route('/v1/tasks',methods=["DELETE"])
def delete_multiple_tasks():


    l=request.get_json()
    l=l["tasks"]
    for i in l:
        db.tasks.delete_one({"id":int(i["id"])})
    return Response(response="None",status=204)

if __name__=='__main__':
    app.run(port=8000,debug=True)
