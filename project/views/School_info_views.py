#Schoolinfoテーブルapi追加:5/20近藤

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from project.models import School_info
from project import db
School_info_bp = Blueprint('School_info', __name__)

#schoolinfoのtable情報取得
@School_info_bp.route('/schools',methods=['GET'])
def get_schools():
    schools = School_info.query.all()
    school_list = []
    for school in schools:
        school_data = {
            'school_id': school.school_id ,
            'user_id' :school.user_id,
            'school_type':school.school_type,
            'school_name':school.school_name,
            'study_line':school.study_line,
            'academic_department':school.academic_department,
            'graduation_date':school.graduation_date
        }
        school_list.append(school_data)
    return jsonify(school_list),200

#schoolの詳細取得
@School_info_bp.route('/schools/<school_id>',methods=['GET'])
def get_school(school_id):
    school = School_info.query.get(school_id)
    if not school:
        return jsonify({"error": "School_info not found."}), 404
    
    school_data={
            'school_id': school.school_id ,
            'user_id' :school.user_id,
            'school_type':school.school_type,
            'school_name':school.school_name,
            'study_line':school.study_line,
            'academic_department':school.academic_department,
            'graduation_date':school.graduation_date
    }
    return jsonify(school_data),200

#schoolの登録
@School_info_bp.route('/school',methods=['POST'])
@jwt_required()
def register_school():
    data = request.get_json()
    school_type = data.get("school_type") 
    school_name = data.get("school_name") 
    study_line = data.get("study_line")
    academic_department = data.get("academic_department")
    current_user = get_jwt_identity()

#必須事項check :学校種別,学校名,studyline,学部,卒業日
    if not  school_type or not school_name or not study_line or not academic_department:
        return jsonify({"error": "school_type, school_name, study_line,  academic_department, and graduation_date are required."}), 400
    
    new_school = School_info(
    school_type = school_type ,
    school_name = school_name ,
    study_line = study_line ,
    academic_department = academic_department ,
    user_id = current_user
    )
    
    db.session.add(new_school)
    db.session.commit()

    return jsonify ({
    'school_id': new_school.school_id ,
    'user_id' : new_school.user_id,
    'school_type':new_school.school_type,
    'school_name':new_school.school_name,
    'study_line':new_school.study_line,
    'academic_department':new_school.academic_department
    }),201
    
    
# School削除
@School_info_bp.route('/schools/<school_id>', methods=['DELETE'])
def delete_school(school_id):
    school = School_info.query.get(school_id)
    if not school:
        return jsonify({"error": "school not found."}), 404

    db.session.delete(school)
    db.session.commit()

    return jsonify({"message":"School_info deleted successfully!"})