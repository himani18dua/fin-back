from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os
import subprocess
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.errorhandler(Exception)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

tasks = {}

@app.route('/members', methods=['GET'])
def members():
    try:
        file_path = os.path.join('output_directory', 'broken_links.json')
        with open(file_path, 'r') as f:
            broken_links = json.load(f)
        return jsonify(broken_links)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/img-members', methods=['GET'])
def img_members():
    try:
        file_path = os.path.join('output_directory', 'images_without_alt.json')
        with open(file_path, 'r') as f:
            images_without_alt = json.load(f)
        return jsonify(images_without_alt)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "URL is required"}), 400

        task_id = str(uuid.uuid4())
        tasks[task_id] = {"state": "PENDING"}

        script_directory = 'myproject/myproject/spiders'
        script_name = 'crawler.py'
        script_path = f'{script_directory}/{script_name}'
        command = ['scrapy', 'runspider', script_path, '-a', f'url={url}']
        subprocess.run(command, text=True)

        tasks[task_id]["state"] = "SUCCESS"  # Or handle as per the actual state of the subprocess
        return jsonify({"task_id": task_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/img-crawl', methods=['POST'])
def imgcrawl():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "URL is required"}), 400

        task_id = str(uuid.uuid4())
        tasks[task_id] = {"state": "PENDING"}

        script_directory = 'myproject/myproject/spiders'
        script_name = 'imgcrawler.py'
        script_path = f'{script_directory}/{script_name}'
        command = ['scrapy', 'runspider', script_path, '-a', f'url={url}']
        subprocess.run(command, text=True)

        tasks[task_id]["state"] = "SUCCESS"  # Or handle as per the actual state of the subprocess
        return jsonify({"task_id": task_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)

@app.route('/img-download')
def download():
    try:
        json_path = 'output_directory/images_without_alt.json'
        pdf_path = 'output_directory/images_without_alt.pdf'

        with open(json_path, 'r') as f:
            data = json.load(f)

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        text = c.beginText(40, height - 40)
        text.setFont("Helvetica", 10)

        json_str = json.dumps(data, indent=4)
        lines = json_str.split('\n')

        for line in lines:
            text.textLine(line)

        c.drawText(text)
        c.save()

        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download')
def download_file():
    try:
        json_path = 'output_directory/broken_links.json'
        pdf_path = 'output_directory/broken_links.pdf'

        with open(json_path, 'r') as f:
            data = json.load(f)

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        text = c.beginText(40, height - 40)
        text.setFont("Helvetica", 10)

        json_str = json.dumps(data, indent=4)
        lines = json_str.split('\n')

        for line in lines:
            text.textLine(line)

        c.drawText(text)
        c.save()

        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0')
