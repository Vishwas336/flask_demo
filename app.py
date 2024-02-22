from flask import Flask,render_template,url_for,request , jsonify
import random
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys

sys.setrecursionlimit(2000)

app = Flask(__name__)

class Point():
    def __init__(self, x, y, wn):
        self.x = x
        self.y = y
        self.wn = wn

class Node():
    def __init__(self, x0, y0, w, h, points):
        self.x0 = x0
        self.y0 = y0
        self.width = w
        self.height = h
        self.points = points
        self.children = []

    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def get_points(self):
        return self.points


def recursive_subdivide(node, k):
    if len(node.points)<=k:
        return
   
    w_ = float(node.width//2.0)
    h_ = float(node.height//2.0)

    p = contains(node.x0, node.y0, w_, h_, node.points)
    x1 = Node(node.x0, node.y0, w_, h_, p)
    recursive_subdivide(x1, k)

    p = contains(node.x0, node.y0+h_, w_, h_, node.points)
    x2 = Node(node.x0, node.y0+h_, w_, h_, p)
    recursive_subdivide(x2, k)

    p = contains(node.x0+w_, node.y0, w_, h_, node.points)
    x3 = Node(node.x0 + w_, node.y0, w_, h_, p)
    recursive_subdivide(x3, k)

    p = contains(node.x0+w_, node.y0+h_, w_, h_, node.points)
    x4 = Node(node.x0+w_, node.y0+h_, w_, h_, p)
    recursive_subdivide(x4, k)

    node.children = [x1, x2, x3, x4]
   
   
def contains(x, y, w, h, points):
    pts = []
    for point in points:
        if point.x >= x and point.x <= x+w and point.y>=y and point.y<=y+h:
            pts.append(point)
    return pts


def find_children(node):
    if not node.children:
        return [node]
    else:
        children = []
        for child in node.children:
            children += (find_children(child))
    return children

import random
import matplotlib.pyplot as plt # plotting libraries
import matplotlib.patches as patches

class QTree():
    def __init__(self, k, n, data_source):
        self.threshold = k
        if data_source == "random":
            self.points = [Point(random.uniform(0, 960), random.uniform(0, 500), random.uniform(0, 1)) for _ in range(n)]
        elif data_source == "random_normal":
            mean, std_dev = 480, 100
            self.points = [Point(np.random.normal(mean, std_dev), np.random.normal(mean, std_dev), random.uniform(0, 1)) for _ in range(n)]
        elif data_source == "csv":
            # Assuming 'data.csv' has columns 'x' and 'y'
            self.points = self.load_csv_data('scaled_points_usa1.csv')
            # Add wn randomly (to be replaced with actual values later)
            for point in self.points:
                point.wn = random.uniform(0, 1)
        else:
            raise ValueError("Invalid data source")
        self.root = Node(0, 0, 960, 500, self.points)

    def add_point(self, x, y):
        self.points.append(Point(x, y))
    
    def get_points(self):
        return self.points
    
    def subdivide(self):
        recursive_subdivide(self.root, self.threshold)
    
    def graph(self):
        fig = plt.figure(figsize=(12, 8))
        plt.title("Quadtree")
        c = find_children(self.root)
        print("Number of segments: %d" %len(c))
        areas = set()
        for el in c:
            areas.add(el.width*el.height)
        print("Minimum segment area: %.3f units" %min(areas))
        for n in c:
            plt.gcf().gca().add_patch(patches.Rectangle((n.x0, n.y0), n.width, n.height, fill=False))
        x = [point.x for point in self.points]
        y = [point.y for point in self.points]
        plt.plot(x, y, 'ro') # plots the points as red dots
        plt.show()
        return
    
    def load_csv_data(self, filename):
        points = []
        with open(filename, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            count = 0
            for row in csv_reader:
                # Assuming columns are 'x' and 'y'
                count += 1
                x = float(row['scaled_x'])
                y = float(row['scaled_y'])
                points.append(Point(x, y, 0))  # Add placeholder 'wn' value
        return points

quadtree = None



@app.route('/', methods=['GET', 'POST'])
def index():
    data_sources = ["random", "random_normal", "csv"]
    selected_data_source = "random"  # Default to random data
    if request.method == 'POST':
        selected_data_source = request.form.get('data_source', 'random')

    global quadtree
    quadtree = QTree(k=2, n=10000, data_source=selected_data_source)
    quadtree.subdivide()
    pts = contains(0, 0, 960, 500, quadtree.get_points())
    data = [(point.x, point.y) for point in pts]
   
    return render_template('index.html', data=data, data_sources=data_sources, selected_data_source=selected_data_source)

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        # Get x0, x1, y0, and y1 values from the request
        data = request.get_json()
        x0 = data['x0']
        x1 = data['x1']
        y0 = data['y0']
        y1 = data['y1']

        # Perform the search using the contains function
        
        pts_search = contains(x0,y0,x1,y1,quadtree.get_points())
        #pts_search = random.sample(pts_search,5000)

        pts_search.sort(key=lambda point: point.wn)

        if len(pts_search) > 5000:
            pts_search = pts_search[:5000]

        # data_search = []
        # for point in pts_search:
        #     data_search.append((point.x, point.y))
    
        data_search = [(point.x, point.y) for point in pts_search]
        data_search+=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        
        # You can return the result as JSON
        return jsonify(data_search)

if __name__ == '__main__':
    app.run(debug=True)