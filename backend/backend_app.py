from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

def get_current_date_time():
    current_date_time = datetime.now().strftime('%y-%m-%d, %H:%M')
    return current_date_time


def read_json_file(file_path):
    try:
        with open(file_path) as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        else:
            raise ValueError('Invalid JSON format')
    except FileNotFoundError:
        raise FileNotFoundError('File not found')
    except Exception as e:
        raise Exception(str(e))


def write_json_file(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        raise Exception(f"Error writing JSON file: {str(e)}")


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    posts = read_json_file('backend/posts.json')
    if request.method == 'GET':
        sort = request.args.get('sort')
        direction = request.args.get('direction')

        if not sort and not direction:
            return jsonify(posts)

        sort_key_functions = {
            'title': lambda post: post['title'],
            'content': lambda post: post['content'],
            'author': lambda post: post['author'],
            'date': lambda post: post['date']
        }

        if sort in sort_key_functions:
            key_function = sort_key_functions[sort]
            sorted_posts = sorted(posts, key=key_function,
                                  reverse=(direction == 'desc'))
            return jsonify(sorted_posts)
        else:
            return jsonify({'message': 'Bad request'}), 400

    elif request.method == 'POST':
        # Process the request to add a new post
        # Assuming the request contains JSON data for the new post
        new_post = request.get_json()
        # Check for missing fields
        if 'title' not in new_post or 'content' not in new_post:
            error_message = "Missing required fields: "
            missing_fields = []
            if 'title' not in new_post:
                missing_fields.append("'title'")
            if 'content' not in new_post:
                missing_fields.append("'content'")
            if 'author' not in new_post:
                missing_fields.append('author')
            error_message += ', '.join(missing_fields)
            response = {'message': error_message}
            return jsonify(response), 400  # Response - 400 (Bad Request)

        if len(posts) > 0:
            new_post_id = max(post['id'] for post in posts) + 1
        else:
            new_post_id = 1
        new_post['id'] = new_post_id
        new_post['date'] = get_current_date_time()
        posts.append(new_post)
        write_json_file(posts, 'backend/posts.json')
        return jsonify(posts), 201  # Return all posts and status 201 (Created)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    posts = read_json_file('backend/posts.json')
    for post in posts:
        if post['id'] == post_id:
            posts.remove(post)
            write_json_file(posts, 'backend/posts.json')
            return jsonify({'message': f'Post with id {post_id} has been '
                                       f'deleted successfully.'}), 200
    return jsonify({'message': 'Post not found'}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    posts = read_json_file('backend/posts.json')
    update_info = request.get_json()
    for post in posts:
        if post['id'] == post_id:
            if len(update_info) > 0:
                for key, value in update_info.items():
                    if key in ['title', 'content', 'author', 'date']:
                        post[key] = value
                write_json_file(posts, 'backend/posts.json')
                return jsonify(post), 200
            else:
                return jsonify(post), 200
        return jsonify({'message': 'Post not found'}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')
    author = request.args.get('author')
    date = request.args.get('date')

    if not title and not content and not author and not date:
        return jsonify({'message': 'No search parameters provided'}), 400

    posts = read_json_file('backend/posts.json')
    matched_posts = []
    for post in posts:
        if title and title.lower() in post['title'].lower():
            matched_posts.append(post)
        if content and content.lower() in post['content'].lower():
            matched_posts.append(post)
        if author and author.lower() in post['author'].lower():
            matched_posts.append(post)
        if date and date.lower() in post['date'].lower():
            matched_posts.append(post)

    if len(matched_posts) == 0:
        return jsonify({'message': 'Post not found'}), 404

    return jsonify(matched_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
