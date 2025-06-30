#Plantテーブル追加:5/23近藤

from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from project.models import GrowthMilestone, GrowthMilestoneLog, Plant
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
@Plant_bp.route('/plant', methods=['GET'])
@jwt_required()
def get_plant():
    current_user = get_jwt_identity()
    plant = Plant.query.filter_by(user_id=current_user).first()
    
    if not plant:
        return jsonify({'message': 'Plant not found'}), 404

    # 初期化
    milestones_data = None

    growth_milestones = GrowthMilestone.query.filter_by(plant_id=plant.plant_id).first()
    if growth_milestones:
        logs = GrowthMilestoneLog.query.filter_by(milestone_id=growth_milestones.milestone_id).all()
        logs_data = [
            {
                'log_id': log.log_id,
                'log_message': log.log_message,
                'created_at': log.created_at
            }
            for log in logs
        ]
        milestones_data = {
            'milestone_id': growth_milestones.milestone_id,
            'milestone': growth_milestones.milestone,
            'level': growth_milestones.level,
            'achieved_at': growth_milestones.achieved_at,
            'logs': logs_data
        }
    plant_data = {
        'plant_id': plant.plant_id,
        'user_id': plant.user_id,
        'growth_stage': plant.growth_stage,
        'mood': plant.mood,
        'last_updated': plant.last_updated,
        'plant_name': plant.plant_name,
        'color': plant.color,
        'size': plant.size,
        'motivation_style': plant.motivation_style,
        'growth_milestones': milestones_data  # None も許容する
    }
    return jsonify(plant_data), 200

@Plant_bp.route('/plant_user/<user_id>', methods=['GET'])
def get_user_plant(user_id):
    plant = Plant.query.filter_by(user_id=user_id).first()
    
    if not plant:
        return jsonify({'message': 'Plant not found'}), 404

    # 初期化
    milestones_data = None

    growth_milestones = GrowthMilestone.query.filter_by(plant_id=plant.plant_id).first()
    if growth_milestones:
        logs = GrowthMilestoneLog.query.filter_by(milestone_id=growth_milestones.milestone_id).all()
        logs_data = [
            {
                'log_id': log.log_id,
                'log_message': log.log_message,
                'created_at': log.created_at
            }
            for log in logs
        ]
        milestones_data = {
            'milestone_id': growth_milestones.milestone_id,
            'milestone': growth_milestones.milestone,
            'level': growth_milestones.level,
            'achieved_at': growth_milestones.achieved_at,
            'logs': logs_data
        }
    plant_data = {
        'plant_id': plant.plant_id,
        'user_id': plant.user_id,
        'growth_stage': plant.growth_stage,
        'mood': plant.mood,
        'last_updated': plant.last_updated,
        'plant_name': plant.plant_name,
        'color': plant.color,
        'size': plant.size,
        'motivation_style': plant.motivation_style,
        'growth_milestones': milestones_data  # None も許容する
    }
    return jsonify(plant_data), 200

#plantの登録
@Plant_bp.route('/plant',methods=['POST'])
@jwt_required()
def register_plant():
    data = request.get_json()
    grows_stage = data.get("growth_stage") 
    mood = data.get("mood")
    color = data.get("color")
    plant_name = data.get("plant_name")
    size = data.get("size")
    motivation_style = data.get("motivation_style")
    current_user = get_jwt_identity()

    #必須事項check 
    if not  grows_stage or not mood:
        return jsonify({"error": "grows_stage, mood and last_updated are required."}), 400
    
    new_plant = Plant(
    growth_stage = grows_stage ,
    user_id = current_user,
    mood = mood ,
    plant_name = plant_name,
    color = color,
    size = size,
    motivation_style = motivation_style,
    )
    
    db.session.add(new_plant)
    db.session.commit()
    print("New plant created:", new_plant.plant_id)
    new_growth_milestone = GrowthMilestone(
        plant_id = new_plant.plant_id,
        milestone = 0,
        level = 1,
    )
    db.session.add(new_growth_milestone)
    db.session.commit()
    new_log = GrowthMilestoneLog(
        milestone_id = new_growth_milestone.milestone_id,
        log_message = "Plant created",
        created_at = new_plant.last_updated
    )
    db.session.add(new_log)
    db.session.commit()

    return jsonify ({
    'plant_id': new_plant.plant_id ,
    'user_id' :new_plant.user_id ,
    'growth_stage':new_plant.growth_stage,
    'mood':new_plant.mood,
    'plant_name':new_plant.plant_name,
    'color': new_plant.color,
    'size': new_plant.size,
    'motivation_style': new_plant.motivation_style,
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

# Plant更新
@Plant_bp.route('/plants', methods=['PUT'])
@jwt_required()
def update_plant():
    current_user = get_jwt_identity()
    data = request.get_json()
    plant = Plant.query.get(user_id=current_user)
    
    if not plant:
        return jsonify({"error": "Plant not found."}), 404

    # 更新可能なフィールドをチェック
    if 'grows_stage' in data:
        plant.grows_stage = data['grows_stage']
    if 'mood' in data:
        plant.mood = data['mood']
    if 'last_updated' in data:
        plant.last_updated = data['last_updated']

    db.session.commit()

    return jsonify({
        'plant_id': plant.plant_id,
        'user_id': plant.user_id,
        'growth_stage': plant.grows_stage,
        'mood': plant.mood,
        'last_updated': plant.last_updated
    }), 200