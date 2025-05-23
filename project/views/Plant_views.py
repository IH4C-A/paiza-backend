#Plantテーブル追加:5/23近藤

from flask import request, jsonify, Blueprint
from project.models import Plant
from project import db
Plant_bp = Blueprint('Plant', __name__)

#schoolinfoのtable情報取得
@Plant_bp.route('/plants',methods=['GET'])
def get_plants():
    plants = Plant.query.all()
    plant_list = []
    for plant in plants:
        plant_data = {
            'plant_id': plant.plant_id ,
            'user_id' :plant.user_id,
            'growth_stage':plant.grows_stage,
            'mood':plant.mood,
            'last_updated':plant.last_updated,
        }
        plant_list.append(plant_data)
    return jsonify(plant_list),200

#schoolの詳細取得
@Plant_bp.route('/plants/<plant_id>',methods=['GET'])
def get_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if not plant:
        return jsonify({"error": " Plant not found."}), 404
    
    plant_data={
            'plant_id': plant.plant_id ,
            'user_id' :plant.user_id,
            'grows_stage':plant.grows_stage,
            'mood':plant.mood,
            'last_updated':plant.last_updated,
    }
    return jsonify(plant_data),200

#plantの登録
@Plant_bp.route('/plant',methods=['GET'])
def register_plant():
    data = request.get_json()
    grows_stage = data.get("grows_stage") 
    mood = data.get("mood") 
    last_updated = data.get("last_updated")

#必須事項check 
    if not  grows_stage or not mood or not last_updated  :
        return jsonify({"error": "grows_stage, mood and last_updated are required."}), 400
    
    new_plant = Plant(
    grows_stage = grows_stage ,
    mood = mood ,
    last_updated = last_updated ,
    )
    
    db.session.add(new_plant)
    db.session.commit()

    return jsonify ({
    'plant_id': new_plant.plant_id ,
    'user_id' :new_plant.user_id ,
    'grows_stage':new_plant.grows_stage,
    'mood':new_plant.mood,
    'last_updated':new_plant.last_updated,
    }),201
    
    
# Plant削除
@Plant_bp.route('/plants/<plant_id>', methods=['DELETE'])
def delete_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if not plant:
        return jsonify({"error": "plant not found."}), 404

    db.session.delete(plant)
    db.session.commit()

    return jsonify({"message": "Plant deleted successfully!"})