from flask import Flask, request, jsonify, render_template, redirect, abort
import json
import os

app = Flask(__name__)
DATA_FILE = 'users.json'

# Function to read data from the JSON file
def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Function to write data to the JSON file
def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# API to update user data via GET query parameters
@app.route('/api/update', methods=['GET'])
def api_update():
    user = request.args.get('user')
    gb = request.args.get('gb')
    gb2 = request.args.get('gb2')
    if not user:
        return jsonify({'error': 'Missing user parameter'}), 400
    data = read_data()
    for u in data:
        if u['user'] == user:
            if gb is not None:
                try:
                    u['gb'] = int(gb)
                except ValueError:
                    return jsonify({'error': 'Invalid gb value'}), 400
            if gb2 is not None:
                try:
                    u['gb2'] = int(gb2)
                except ValueError:
                    return jsonify({'error': 'Invalid gb2 value'}), 400
            write_data(data)
            return jsonify({'message': 'Updated successfully'})
    return jsonify({'error': 'User not found'}), 404

# API to list all users
@app.route('/api/users', methods=['GET'])
def api_get_users():
    data = read_data()
    return jsonify(data)

# API to get a specific user
@app.route('/api/users/<user>', methods=['GET'])
def api_get_user(user):
    data = read_data()
    for u in data:
        if u['user'] == user:
            return jsonify(u)
    return jsonify({'error': 'User not found'}), 404

# API to create a new user
@app.route('/api/users', methods=['POST'])
def api_create_user():
    if request.form:
        new_user = request.form.to_dict()
    elif request.json:
        new_user = request.json
    else:
        return jsonify({'error': 'No data provided'}), 400
    if 'user' not in new_user or 'gb' not in new_user or 'gb2' not in new_user:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        new_user['gb'] = int(new_user['gb'])
        new_user['gb2'] = int(new_user['gb2'])
    except ValueError:
        return jsonify({'error': 'Invalid gb or gb2 value'}), 400
    data = read_data()
    for u in data:
        if u['user'] == new_user['user']:
            return jsonify({'error': 'User already exists'}), 409
    data.append(new_user)
    write_data(data)
    return redirect('/admin/mc97')

# API to update or delete a user
@app.route('/api/users/<user>', methods=['POST'])
def api_update_or_delete_user(user):
    data = read_data()
    user_data = next((u for u in data if u['user'] == user), None)
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    if request.form.get('_method') == 'DELETE':
        data.remove(user_data)
        write_data(data)
        return redirect('/')
    else:
        if request.form:
            update_data = request.form.to_dict()
        elif request.json:
            update_data = request.json
        else:
            return jsonify({'error': 'No data provided'}), 400
        if 'gb' in update_data:
            try:
                user_data['gb'] = int(update_data['gb'])
            except ValueError:
                return jsonify({'error': 'Invalid gb value'}), 400
        if 'gb2' in update_data:
            try:
                user_data['gb2'] = int(update_data['gb2'])
            except ValueError:
                return jsonify({'error': 'Invalid gb2 value'}), 400
        write_data(data)
        return redirect('/admin/mc97')

# Web page to list all users
@app.route('/admin/mc97')
def admin():
    data = read_data()
    return render_template('admin.html', users=data)

# Web page to list all users
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user = request.form.get('user')
        if user:
            return redirect(f'/{user}')
        return render_template('index.html', error="Please enter a username")
    return render_template('index.html')

# Web page to display a specific user's details
@app.route('/<user>')
def user_page(user):
    data = read_data()
    for u in data:
        if u['user'] == user:
            return render_template('user.html', user=user, gb=u['gb'], gb2=u['gb2'])
    abort(404)

# Custom 404 handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=80)