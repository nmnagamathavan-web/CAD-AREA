from flask import Flask, render_template, request
import ezdxf
import math
import os

# Conversion constants
CENT = 40.468564224  # 1 cent = 40.4685 m²
ACRE = 4046.8564224  # 1 acre = 4046.85 m²

app = Flask(__name__)

# Shoelace formula for polygon area
def polygon_area(points):
    n = len(points)
    area = 0
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    user_name = request.form["user_name"]
    file = request.files["dxfFile"]

    if file:
        filepath = "uploaded.dxf"
        file.save(filepath)

        # Read DXF file
        doc = ezdxf.readfile(filepath)
        msp = doc.modelspace()

        total_area = 0

        # Loop through polylines
        for pline in msp.query("LWPOLYLINE"):
            points = [(p[0], p[1]) for p in pline.get_points()]
            area = polygon_area(points)
            total_area += area
            
            
        lines = msp.query("LINE")
        if lines:
            points = []
            for line in lines:
                start = (line.dxf.start.x, line.dxf.start.y)
                end = (line.dxf.end.x, line.dxf.end.y)
                if start not in points:
                    points.append(start)
                if end not in points:
                    points.append(end)

            # Compute area only if polygon is valid
            if len(points) >= 3:
                total_area += polygon_area(points)
                    
                
          

        # Convert to cent & acre
        area_in_cent = total_area / CENT
        area_in_acre = total_area / ACRE

        # Cleanup (optional)
        os.remove(filepath)

        return f"""
        <h2>Hello {user_name}!</h2>
        <p>DXF file processed successfully ✅</p>
        <p><b>Total Area:</b> {total_area:.2f} m²</p>
        <p><b>In Cent:</b> {area_in_cent:.2f} cent</p>
        <p><b>In Acre:</b> {area_in_acre:.4f} acre</p>
        """
    else:
        return "❌ No file uploaded!"

if __name__ == "__main__":
    app.run(debug=True)
