from flask import Blueprint, render_template, request, jsonify
from app import searcher

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "")
    results = []
    if query:
        results = searcher.search(query_text=query, top_k=5, threshold=0.1)
    return render_template("index.html", query=query, results=results)

@main.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json() or {}
    query = data.get("query", "")
    results = searcher.search(query_text=query, top_k=5, threshold=0.1)
    return jsonify({"query": query, "results": results})