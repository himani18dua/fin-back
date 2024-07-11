from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import json
import os
from scrapy.crawler import CrawlerProcess

# Import your Scrapy spiders here
from myproject.myproject.spiders.crawler import FindBrokenSpider
from myproject.myproject.spiders.imgcrawler import FindImagesWithoutAltSpider
from scrapy.utils.project import get_project_settings

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "https://frontend-react-31ahnhmpk-hds-projects-a2b29e6e.vercel.app/"}})
@app.route('/crawl', methods=['POST'])
@cross_origin()
def crawl():
    try:
        data = request.get_json()
        url = data.get('url')
        print(url)

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Run the Scrapy spider programmatically
        process = CrawlerProcess(get_project_settings())
        process.crawl(FindBrokenSpider, url=url)
        process.start()


        return jsonify({"message": "Crawling started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/img-crawl', methods=['POST'])
@cross_origin()
def imgcrawl():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "URL is required"}), 400

        # Run the Scrapy spider programmatically
        print(url)
       
        process = CrawlerProcess(get_project_settings())
        process.crawl(FindImagesWithoutAltSpider, url=url)
        process.start()

        return jsonify({"message": "Crawling started"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/img-members', methods=['GET'])
@cross_origin()
def img_members():
    file_path = os.path.join('output_directory', 'images_without_alt.json')
    with open(file_path, 'r') as f:
        images_without_alt = json.load(f)
    return jsonify(images_without_alt)

    
@app.route("/members", methods=['GET'])
@cross_origin()
def members():
    
    print('hello')
    file_path = os.path.join('output_directory', 'broken_links.json')
    print(file_path)

    with open(file_path, 'r') as f:
        broken_links = json.load(f)

    return broken_links

@app.route('/download')
@cross_origin()
def download_file():
    json_path = 'output_directory/broken_links.json'
    pdf_path = 'output_directory/broken_links.pdf'

    # Load JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Create a PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    text = c.beginText(40, height - 40)
    text.setFont("Helvetica", 10)

    # Convert JSON data to text
    json_str = json.dumps(data, indent=4)
    lines = json_str.split('\n')

    # Add text to PDF
    for line in lines:
        text.textLine(line)

    c.drawText(text)
    c.save()

    # Send the PDF file as a response
    return send_file(pdf_path, as_attachment=True)

@app.route('/img-download')
@cross_origin()
def download_images_file():
    json_path = 'output_directory/images_without_alt.json'
    pdf_path = 'output_directory/images_without_alt.pdf'

    # Load JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Create a PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    text = c.beginText(40, height - 40)
    text.setFont("Helvetica", 10)

    # Convert JSON data to text
    json_str = json.dumps(data, indent=4)
    lines = json_str.split('\n')

    # Add text to PDF
    for line in lines:
        text.textLine(line)

    c.drawText(text)
    c.save()

    # Send the PDF file as a response
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
