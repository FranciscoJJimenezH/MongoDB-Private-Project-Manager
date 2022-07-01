#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import subprocess
import json
import datetime
import platform

from collections import ChainMap
import gridfs

class DBManager:
    
    def __init__(self, db, tp):
        self.db = db
        self.tp = tp   
        
    @staticmethod
    def new_register():
        try:
            DBManager.remove_register()
        finally:
            if platform.system() == 'Linux':
                subprocess.Popen(["gnome-terminal -- python3 register.py"], shell=True)
            else:
                subprocess.Popen(['start','register.py'], shell=True)
            
    @staticmethod
    def remove_register():
        subprocess.Popen(["rm -fr unit.json"], shell=True)    
        
    @staticmethod
    def add_register(db, tp, info, e=[]):
        reg = [{'db': db, 'tp': tp, 'info': f'from {info}'}, 'DONE']
        if e:
            reg[0]['e'] = e
            reg[1] = 'ERROR'
        
        try:
            with open('unit.json', "r+") as file:
                data = json.load(file)
                data.append(reg)
                file.seek(0)
                json.dump(data, file)
        except FileNotFoundError: pass
        except Exception: pass
        
    def __call__(self, action):
        
        def wrapper(*args, **kwargs):
            pass

            # client = MongoClient('mongodb://FRENCHITOSTARK:industries@127.0.0.1')#FRENCHITOSTARK:industries
            # db = client[self.db]
            # ar = None
            # try:
            #     ar = action(*args, **kwargs, db=db)
            #     self.add_register(self.db, self.tp, action.__name__)
                
            # except Exception as e: 
            #     self.add_register(self.db, self.tp, action.__name__, e)
            #     raise Exception(e)
                
            # client.close()
            # return ar
        
        return wrapper

class MomentDBManager:
    
    @DBManager('PasiveMoments', 'GET')
    def get_last_update(self,collx, db):
        
        try:
            res = db[collx].find({'_id': 'info'})[0]
            return res
        except:
            last_update = datetime.datetime(1980,1,1)
            res = {
                '_id': 'info',
                'last_update': last_update,
                'qy': {}
            }
            db[collx].insert_one(res)
            return res
    
    @DBManager('PasiveMoments', 'GET')
    def get_lyx(self, collx, docx, db):
        
        return db[collx].find({'_id':f'lyx/{docx}'})[0]['lyx']
    
    @DBManager('PasiveMoments', 'GET')
    def get_dlyx(self, collx, docx, db):
        
        return db[collx].find({'_id':f'dlyx/{docx}'})[0]['dlyx']
    
    @DBManager('PasiveMoments', 'UPDATE')
    def update_last_update(self,collx, test, db):
        
        db[collx].update_one({'_id': 'info'}, {
            '$set': {
                'last_update': datetime.datetime(2010,1,1) if test else datetime.datetime.now(),
            }
        })
    
    
    @DBManager('PasiveMoments', 'UPDATE')
    def update_lyx(self, collx, docx, lyx, db):
        
        _id =  f'lyx/{docx}'
        udata = {'lyx': lyx}
        
        if len(list(db[collx].find({'_id': _id}))) >= 1:
            db[collx].update_one( {'_id': _id}, { '$push': udata } )
            
        else:
            db[collx].insert_one(dict(ChainMap({'_id': _id}, udata)))
            
    @DBManager('PasiveMoments', 'UPDATE')
    def update_dlyx(self, collx, docx, dlyx, db):
        pass
    
    @DBManager('PasiveMoments', 'UPDATE')
    def update_process_qy(self, collx, docx, qy, db):
        db[collx].update_one({'_id': 'info'}, {
            '$set': { 
                f'qy.{docx}': qy
            }
        })
        
class PatternDBManager:
    
    @DBManager('ActivePatterns', 'GET')
    def get_patterns(self, collx, docx, lyx, db):
        dbb = db[collx].find({'_id': docx})[0]
        return dbb
    
    @DBManager('Activeelations', 'GET')
    def get_relations(self, db):
        pass
    
    @DBManager('ActivePatterns', 'UPDATE')
    def update_patterns(self, collx, docx, sets, tp, db):
        
        ref = f'{docx}/{tp}'
        if len(list(db[collx].find({'_id': ref}))) >= 1:
            db[collx].update_one( {'_id': ref}, { '$set': sets } )
            
        else:
            db[collx].insert_one(dict(ChainMap({'_id': ref},sets)))
    
    @DBManager('ActiveRelations', 'UPDATE')
    def update_relations(self, db):
        pass
    
    @DBManager('PasiveMoments', 'UPDATE')
    def update_sequence(self, db):
        pass
    
    @DBManager('PasiveMoments', 'UPDATE')
    def update_time_changed(self, db):
        pass
    
    @DBManager('PasiveMoments', 'UPDATE')
    def search_for_relation(self, db):
        pass

class ProjectorDBManager:
    pass

class SRegimeDBManager:
    
    pass
       
class GRegimeDBManager:
    pass

class OptDBManager:
    pass

class ModelManager:
    
    @DBManager('ModelInfo', 'UPDATE')
    def update_init(self, db):
        
        db['model'].insert_one({
            '_id': 'info',
            'state': 'OFF',
        })
        db['model'].insert_one({
            '_id': 'units', 
            'units_info': []
        })
        
    @DBManager('ModelInfo', 'GET')
    def get_init(self, db):

        try:
            self.get_state()
            return True
        except:
            return False
    
    
    @DBManager('ModelInfo', 'GET')
    def get_state(self, db):
        return db['model'].find({'_id': 'info'})[0]['state']
    
    @DBManager('ModelInfo', 'GET')
    def get_units(self, db):

        return db['model'].find({'_id':'units'})[0]
    
    @DBManager('ModelInfo', 'PUSH')
    def add_unit(self, db):

        units = self.get_units()
        unit_id = len(units['units_info'])
        
        unit_info = {
            'id': unit_id,
            'state':'ON',
            'tickets':[]
        }
        db['model'].update_one({'_id': 'units'}, {'$push': {'units_info': unit_info }})
        return unit_id
        
    @DBManager('ModelInfo', 'PULL')
    def remove_unit(self, unit_id, db):

        db['model'].update_one({'_id':'units'}, {'$pull': {'units_info': {'id':unit_id}}})


# client = MongoClient('mongodb://FRENCHITOSTARK:industries@127.0.0.1')#FRENCHITOSTARK:industries
# fs = gridfs.GridFS(client['PasiveMoments'])
# a = fs.put( {'filename':"foo", 'bar':"baz"})
# b = fs.put(fs.get(a), filename="foo", bar="baz")

# out = fs.get(b)
# print(out.read())
# query = {'words':{'$elemMatch':{'0':word['_id']}}}
# db = client['PasiveMoments']['XOM/1-DAY'].find({'_id': 'Open/COMPLETE-RELATIONS'}).find()
# print(db)
