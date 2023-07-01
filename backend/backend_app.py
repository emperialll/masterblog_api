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
            return jsonify({'message': 'Post with id <id> has been deleted '
                                       'successfully.'}), 200
    return jsonify({'message': 'Post not found'}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
