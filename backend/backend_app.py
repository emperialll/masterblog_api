from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'GET':
        return jsonify(POSTS)
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
            error_message += ', '.join(missing_fields)
            response = {'message': error_message}
            return jsonify(response), 400  # Response - 400 (Bad Request)

        new_post_id = max(post['id'] for post in POSTS) + 1
        new_post['id'] = new_post_id
        POSTS.append(new_post)
        return jsonify(POSTS), 201  # Return all posts and status 201 (Created)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    for post in POSTS:
        if post['id'] == post_id:
            POSTS.remove(post)
            return jsonify({'message': f'Post with id {post_id} has been '
                                       f'deleted successfully.'}), 200
    return jsonify({'message': 'Post not found'}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    update_info = request.get_json()
    for post in POSTS:
        if post['id'] == post_id:
            if len(update_info) == 2:
                post['title'] = update_info['title']
                post['content'] = update_info['content']
                return jsonify(post), 200
            else:
                if 'title' in update_info:
                    post['title'] = update_info['title']
                    return jsonify(post), 200
                elif 'content' in update_info:
                    post['content'] = update_info['content']
                    return jsonify(post), 200
    return jsonify({'message': 'Post not found'}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')

    if not title and not content:
        return jsonify({'message': 'No search parameters provided'}), 400

    matched_posts = []
    for post in POSTS:
        if title and title.lower() in post['title'].lower():
            matched_posts.append(post)
        if content and content.lower() in post['content'].lower():
            matched_posts.append(post)
        else:
            return jsonify({'message': 'Post not found'}), 404

    return jsonify(matched_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
