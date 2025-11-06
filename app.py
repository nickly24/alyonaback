from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app, resources={r"/*": {"origins": "*"}})
# Используем threading режим для работы с gunicorn (лучше всего работает)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# MongoDB connection
MONGO_URI = "mongodb://gen_user:I_OBNu~9oHF0(m@81.200.148.71:27017/auth_db?authSource=admin&directConnection=true"
client = MongoClient(MONGO_URI)
db = client.auth_db

# Хранилище активных пользователей и звонков
active_users = {}
call_rooms = {}

# Разрешенные пользователи
ALLOWED_USERS = ['alyona', 'kolia']

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint для Timeweb"""
    return jsonify({
        'status': 'ok',
        'message': 'Alyona Time API is running'
    }), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """Получить список пользователей"""
    return jsonify({'users': ALLOWED_USERS})

@app.route('/api/user/<username>', methods=['GET'])
def get_user(username):
    """Получить информацию о пользователе"""
    if username not in ALLOWED_USERS:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = db.users.find_one({'username': username})
    if not user_data:
        # Создать пользователя, если его нет
        db.users.insert_one({
            'username': username,
            'online': False,
            'in_call': False
        })
        return jsonify({
            'username': username,
            'online': False,
            'in_call': False
        })
    
    return jsonify({
        'username': user_data['username'],
        'online': user_data.get('online', False),
        'in_call': user_data.get('in_call', False)
    })

@socketio.on('connect')
def handle_connect():
    """Обработка подключения"""
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения"""
    print(f'Client disconnected: {request.sid}')
    # Удаляем пользователя из активных
    username = None
    for user, sid in active_users.items():
        if sid == request.sid:
            username = user
            break
    
    if username:
        del active_users[username]
        db.users.update_one(
            {'username': username},
            {'$set': {'online': False, 'in_call': False}}
        )
        
        # Проверяем, был ли пользователь в звонке
        room_id = 'call_room'
        if room_id in call_rooms and username in call_rooms[room_id]['users']:
            call_rooms[room_id]['users'].remove(username)
            if len(call_rooms[room_id]['users']) > 0:
                # Уведомляем оставшегося пользователя
                remaining_user = call_rooms[room_id]['users'][0]
                if remaining_user in active_users:
                    socketio.emit('user_left_call', {
                        'username': username,
                        'message': f'{username} отключился'
                    }, room=active_users[remaining_user])
            del call_rooms[room_id]
        
        # Уведомляем другого пользователя
        socketio.emit('user_disconnected', {'username': username}, broadcast=True)

@socketio.on('user_login')
def handle_user_login(data):
    """Пользователь входит в систему"""
    username = data.get('username')
    if username not in ALLOWED_USERS:
        emit('error', {'message': 'Invalid username'})
        return
    
    active_users[username] = request.sid
    db.users.update_one(
        {'username': username},
        {'$set': {'online': True, 'in_call': False}},
        upsert=True
    )
    
    emit('login_success', {'username': username})
    # Уведомляем другого пользователя о входе
    socketio.emit('user_online', {'username': username}, broadcast=True)
    
    # Проверяем, есть ли ожидающий звонок
    check_pending_call(username)

@socketio.on('join_call')
def handle_join_call(data):
    """Пользователь хочет присоединиться к звонку"""
    username = data.get('username')
    if username not in ALLOWED_USERS:
        emit('error', {'message': 'Invalid username'})
        return
    
    # Определяем другого пользователя
    other_user = 'alyona' if username == 'kolia' else 'kolia'
    
    # Создаем или присоединяемся к комнате звонка
    room_id = 'call_room'
    
    if room_id not in call_rooms:
        # Первый пользователь
        call_rooms[room_id] = {
            'users': [username],
            'status': 'waiting',
            'first_user': username
        }
        join_room(room_id)
        emit('call_waiting', {
            'message': f'Ожидание подключения {other_user}...',
            'room_id': room_id,
            'is_initiator': True
        })
    else:
        # Второй пользователь присоединился
        call_rooms[room_id]['users'].append(username)
        call_rooms[room_id]['status'] = 'active'
        join_room(room_id)
        
        # Уведомляем обоих пользователей, что звонок начался
        first_user = call_rooms[room_id]['first_user']
        # Отправляем каждому пользователю его статус инициатора
        for user in call_rooms[room_id]['users']:
            socketio.emit('call_started', {
                'room_id': room_id,
                'users': call_rooms[room_id]['users'],
                'is_initiator': (user == first_user)
            }, room=active_users[user])
    
    db.users.update_one(
        {'username': username},
        {'$set': {'in_call': True}}
    )

@socketio.on('leave_call')
def handle_leave_call(data):
    """Пользователь покидает звонок"""
    username = data.get('username')
    room_id = data.get('room_id', 'call_room')
    
    leave_room(room_id)
    
    if room_id in call_rooms:
        if username in call_rooms[room_id]['users']:
            call_rooms[room_id]['users'].remove(username)
        
        if len(call_rooms[room_id]['users']) == 0:
            # Удаляем комнату, если никого не осталось
            del call_rooms[room_id]
        else:
            # Уведомляем оставшегося пользователя
            remaining_user = call_rooms[room_id]['users'][0]
            if remaining_user in active_users:
                socketio.emit('user_left_call', {
                    'username': username,
                    'message': f'{username} покинул звонок'
                }, room=active_users[remaining_user])
            # Удаляем комнату, так как остался только один пользователь
            del call_rooms[room_id]
    
    db.users.update_one(
        {'username': username},
        {'$set': {'in_call': False}}
    )

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    """Передача WebRTC offer"""
    username = data.get('username')
    offer = data.get('offer')
    room_id = data.get('room_id', 'call_room')
    
    # Отправляем offer другому пользователю
    socketio.emit('webrtc_offer', {
        'offer': offer,
        'from': username
    }, room=room_id, include_self=False)

@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    """Передача WebRTC answer"""
    username = data.get('username')
    answer = data.get('answer')
    room_id = data.get('room_id', 'call_room')
    
    # Отправляем answer другому пользователю
    socketio.emit('webrtc_answer', {
        'answer': answer,
        'from': username
    }, room=room_id, include_self=False)

@socketio.on('webrtc_ice_candidate')
def handle_webrtc_ice_candidate(data):
    """Передача ICE candidate"""
    username = data.get('username')
    candidate = data.get('candidate')
    room_id = data.get('room_id', 'call_room')
    
    # Отправляем ICE candidate другому пользователю
    socketio.emit('webrtc_ice_candidate', {
        'candidate': candidate,
        'from': username
    }, room=room_id, include_self=False)

def check_pending_call(username):
    """Проверяет, есть ли ожидающий звонок"""
    room_id = 'call_room'
    if room_id in call_rooms and call_rooms[room_id]['status'] == 'waiting':
        other_user = call_rooms[room_id]['users'][0]
        if other_user != username:
            # Есть ожидающий звонок от другого пользователя
            socketio.emit('pending_call', {
                'from': other_user
            }, room=active_users[username])

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 80))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)

