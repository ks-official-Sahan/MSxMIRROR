from pymongo import MongoClient 

class primedb: 
     def __init__(self, name, collection_name): 
         self.client = MongoClient('mongodb+srv://MR-X-HARI:MR-X-HARI@cluster0.up3fecd.mongodb.net/?retryWrites=true&w=majority') 
         self.db = self.client[name] 
         self.collection = self.db[collection_name] 
     def update_shortner(self,id,shortner):
         userdata = dict(id=id, shortner=None) 
         self.collection.insert_one(userdata) 
         self.collection.update_one({"id": id}, {"$set": {'shortner':shortner}})
     def shortner(self, id):
         user = self.collection.find_one({'id': int(id)}) 
         return user.get('shortner', None) 
         
db = primedb('prime','primee')
