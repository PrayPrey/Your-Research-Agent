#!/usr/bin/env python3
"""
H-E1 Expert Rating Interface
Flask web server for collecting expert compliance ratings.
"""
import os
import csv
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file

app = Flask(__name__, template_folder='../templates')

CORPUS_DIR = Path(__file__).parent.parent / 'data' / 'benchmark_metadata_corpus'
RATINGS_CSV = CORPUS_DIR / 'ground_truth_labels.csv'

def init_csv():
    """Initialize CSV file with header"""
    if not RATINGS_CSV.exists():
        CORPUS_DIR.mkdir(parents=True, exist_ok=True)
        with open(RATINGS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'benchmark_name', 'data_realness', 'eval_automation', 
                'infra_readiness', 'rater_id', 'timestamp', 'justification'
            ])

@app.route('/')
def index():
    """List all benchmarks"""
    benchmarks_dir = CORPUS_DIR / 'benchmarks'
    if not benchmarks_dir.exists():
        return "No benchmarks found. Run collect_metadata.py first.", 404
    
    benchmarks = [d.name for d in benchmarks_dir.iterdir() if d.is_dir()]
    
    html = "<h1>Benchmark Rating Dashboard</h1><ul>"
    for bench in sorted(benchmarks):
        html += f'<li><a href="/rate/{bench}">{bench}</a></li>'
    html += "</ul><br><a href='/export'>Export Ratings (CSV)</a>"
    
    return html

@app.route('/rate/<benchmark_name>', methods=['GET', 'POST'])
def rate_benchmark(benchmark_name):
    """Rating form for a specific benchmark"""
    bench_dir = CORPUS_DIR / 'benchmarks' / benchmark_name
    
    if not bench_dir.exists():
        return f"Benchmark {benchmark_name} not found", 404
    
    if request.method == 'POST':
        # Save rating
        data = {
            'benchmark_name': benchmark_name,
            'data_realness': float(request.form['data_realness']),
            'eval_automation': float(request.form['eval_automation']),
            'infra_readiness': float(request.form['infra_readiness']),
            'rater_id': request.form['rater_id'],
            'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'justification': request.form['justification']
        }
        
        save_rating(data)
        return redirect(url_for('index'))
    
    # Load metadata
    metadata = {}
    metadata_file = bench_dir / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
    
    # Check available sources
    sources = {
        'paper': (bench_dir / 'paper.pdf').exists(),
        'readme': (bench_dir / 'README.md').exists(),
        'code': (bench_dir / 'eval_script.py').exists()
    }
    
    return render_template(
        'rate_benchmark.html',
        benchmark_name=benchmark_name,
        metadata=metadata,
        sources=sources
    )

@app.route('/view/<benchmark_name>/<filename>')
def view_file(benchmark_name, filename):
    """Serve benchmark files for viewing"""
    file_path = CORPUS_DIR / 'benchmarks' / benchmark_name / filename
    if not file_path.exists():
        return f"File {filename} not found", 404
    
    if filename.endswith('.pdf'):
        return send_file(file_path, mimetype='application/pdf')
    elif filename.endswith('.md'):
        with open(file_path) as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    elif filename.endswith('.py'):
        with open(file_path) as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    else:
        return send_file(file_path)

@app.route('/export')
def export_ratings():
    """Export ratings CSV"""
    if not RATINGS_CSV.exists():
        return "No ratings found", 404
    return send_file(RATINGS_CSV, as_attachment=True)

def save_rating(data: dict) -> None:
    """Append rating to CSV"""
    init_csv()
    
    with open(RATINGS_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            data['benchmark_name'],
            data['data_realness'],
            data['eval_automation'],
            data['infra_readiness'],
            data['rater_id'],
            data['timestamp'],
            data['justification']
        ])

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Expert rating interface')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    args = parser.parse_args()
    
    init_csv()
    print(f"\nRating interface starting at http://localhost:{args.port}")
    print("Navigate to http://localhost:{}/".format(args.port))
    
    app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()
