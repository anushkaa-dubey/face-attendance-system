import os
import math
from PIL import Image, ImageDraw, ImageFont

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

# Colors - Simple Black & White / Monochrome
BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
FILL_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
SUBTEXT_COLOR = (60, 60, 60)
ALT_FILL = (248, 248, 248)

try:
    FONT_TITLE = ImageFont.truetype("arial.ttf", 24)
    FONT_HEADER = ImageFont.truetype("arialbd.ttf", 18)
    FONT_BODY = ImageFont.truetype("arial.ttf", 15)
    FONT_SMALL = ImageFont.truetype("arial.ttf", 13)
    FONT_LABEL = ImageFont.truetype("arialbd.ttf", 14)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_HEADER = ImageFont.load_default()
    FONT_BODY = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
    FONT_LABEL = ImageFont.load_default()

def draw_arrow_head(draw, p1, p2, size=10):
    x1, y1 = p1
    x2, y2 = p2
    angle = math.atan2(y2 - y1, x2 - x1)
    a1 = (x2 - size * math.cos(angle - math.pi / 6), y2 - size * math.sin(angle - math.pi / 6))
    a2 = (x2 - size * math.cos(angle + math.pi / 6), y2 - size * math.sin(angle + math.pi / 6))
    draw.polygon([p2, a1, a2], fill=LINE_COLOR)

def draw_path_with_arrow(draw, points, label="", label_pos=None):
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=LINE_COLOR, width=2)
    
    if len(points) >= 2:
        draw_arrow_head(draw, points[-2], points[-1])
        
    if label:
        if label_pos is None:
            mid_x = (points[0][0] + points[1][0]) / 2
            mid_y = (points[0][1] + points[1][1]) / 2
            label_pos = (mid_x, mid_y)
        
        lx, ly = label_pos
        bbox = FONT_LABEL.getbbox(label)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        
        draw.rectangle([lx - w/2 - 4, ly - h/2 - 2, lx + w/2 + 4, ly + h/2 + 2], fill=BG_COLOR, outline=LINE_COLOR, width=1)
        draw.text((lx - w/2, ly - h/2 - 1), label, fill=TEXT_COLOR, font=FONT_LABEL)

def draw_box(draw, bbox, title, body_lines=[], is_rounded=True):
    x1, y1, x2, y2 = bbox
    if is_rounded:
        draw.rounded_rectangle(bbox, radius=10, fill=FILL_COLOR, outline=LINE_COLOR, width=2)
    else:
        draw.rectangle(bbox, fill=FILL_COLOR, outline=LINE_COLOR, width=2)
        
    t_bbox = FONT_HEADER.getbbox(title)
    tw = t_bbox[2] - t_bbox[0]
    cx = (x1 + x2) / 2
    draw.text((cx - tw/2, y1 + 12), title, fill=TEXT_COLOR, font=FONT_HEADER)
    
    curr_y = y1 + 38
    if body_lines:
        draw.line([(x1 + 10, curr_y), (x2 - 10, curr_y)], fill=LINE_COLOR, width=1)
        curr_y += 10
        for line in body_lines:
            b_bbox = FONT_BODY.getbbox(line)
            bw = b_bbox[2] - b_bbox[0]
            draw.text((cx - bw/2, curr_y), line, fill=SUBTEXT_COLOR, font=FONT_BODY)
            curr_y += 20

def draw_diamond(draw, bbox, text_lines=[]):
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    
    pts = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
    draw.polygon(pts, fill=ALT_FILL, outline=LINE_COLOR)
    for i in range(4):
        draw.line([pts[i], pts[(i+1)%4]], fill=LINE_COLOR, width=2)
        
    total_h = len(text_lines) * 18
    start_y = cy - total_h / 2
    for line in text_lines:
        b_bbox = FONT_BODY.getbbox(line)
        bw = b_bbox[2] - b_bbox[0]
        draw.text((cx - bw/2, start_y), line, fill=TEXT_COLOR, font=FONT_BODY)
        start_y += 18

def draw_ellipse_node(draw, bbox, title):
    draw.ellipse(bbox, fill=FILL_COLOR, outline=LINE_COLOR, width=2)
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    b_bbox = FONT_HEADER.getbbox(title)
    bw, bh = b_bbox[2] - b_bbox[0], b_bbox[3] - b_bbox[1]
    draw.text((cx - bw/2, cy - bh/2 - 2), title, fill=TEXT_COLOR, font=FONT_HEADER)


# ==========================================
# 1. GENERATE SYSTEM ARCHITECTURE DIAGRAM
# ==========================================
def create_system_architecture_png(filename):
    W, H = 1300, 850
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Main Title
    t_text = "FACE ATTENDANCE SYSTEM - SYSTEM ARCHITECTURE"
    tb = FONT_TITLE.getbbox(t_text)
    draw.text(((W - (tb[2] - tb[0])) / 2, 25), t_text, fill=TEXT_COLOR, font=FONT_TITLE)
    draw.line([(50, 65), (W - 50, 65)], fill=LINE_COLOR, width=2)
    
    # Subsystem Containers
    draw.rounded_rectangle([40, 90, 310, 780], radius=12, fill=BG_COLOR, outline=LINE_COLOR, width=1)
    draw.text((60, 105), "CLIENT TIER", fill=TEXT_COLOR, font=FONT_HEADER)
    
    draw.rounded_rectangle([340, 90, 650, 780], radius=12, fill=BG_COLOR, outline=LINE_COLOR, width=1)
    draw.text((360, 105), "FASTAPI BACKEND TIER", fill=TEXT_COLOR, font=FONT_HEADER)
    
    draw.rounded_rectangle([680, 90, 970, 780], radius=12, fill=BG_COLOR, outline=LINE_COLOR, width=1)
    draw.text((700, 105), "AI MODEL ENGINE", fill=TEXT_COLOR, font=FONT_HEADER)

    draw.rounded_rectangle([1000, 90, 1260, 780], radius=12, fill=BG_COLOR, outline=LINE_COLOR, width=1)
    draw.text((1020, 105), "STORAGE & MEMORY", fill=TEXT_COLOR, font=FONT_HEADER)
    
    # Nodes in Client Tier
    draw_box(draw, [60, 160, 290, 270], "React Native App", ["Mobile UI (Expo)", "Camera Capture", "Server Config Modal"])
    draw_box(draw, [60, 320, 290, 420], "HTTP API Client", ["multipart/form-data", "JSON requests", "Async fetch API"])
    draw_box(draw, [60, 620, 290, 730], "Attendance View", ["Displays History", "Status Cards", "Live Alerts"])

    # Connections inside Client
    draw_path_with_arrow(draw, [(175, 270), (175, 320)])
    draw_path_with_arrow(draw, [(175, 420), (175, 620)])

    # Nodes in Backend Tier
    draw_box(draw, [360, 160, 630, 270], "FastAPI App Router", ["backend/main.py", "CORS Middleware", "Lifespan Startup Handler"])
    draw_box(draw, [360, 310, 630, 420], "Recognition Route", ["POST /recognize", "Validate image bytes", "Orchestrate Detection & Match"])
    draw_box(draw, [360, 460, 630, 560], "Attendance Route", ["POST /attendance", "GET /attendance", "Duplicate Check Logic"])
    draw_box(draw, [360, 620, 630, 730], "SQLAlchemy Session", ["backend/database.py", "get_db() dependency", "SQLite Connection Engine"])

    # Connections inside Backend
    draw_path_with_arrow(draw, [(495, 270), (495, 310)])
    draw_path_with_arrow(draw, [(495, 420), (495, 460)])
    draw_path_with_arrow(draw, [(495, 560), (495, 620)])

    # Nodes in AI Model Engine
    draw_box(draw, [700, 160, 950, 280], "Face Detector (SCRFD)", ["models/scrfd_500m.onnx", "Confidence Cutoff: 0.5", "Outputs Face Bounding Box", "Aligns 5 Facial Landmarks"])
    draw_box(draw, [700, 340, 950, 460], "Face Recognizer", ["models/w600k_mbf.onnx", "MobileFaceNet ArcFace", "Input: Aligned Face Crop", "Output: 512D Vector"])
    draw_box(draw, [700, 520, 950, 640], "Cosine Matcher", ["Calculates Cosine Sim", "Sim Threshold: 0.5", "Finds Max Similarity", "Identifies Person Name"])

    # Connections inside AI Engine
    draw_path_with_arrow(draw, [(825, 280), (825, 340)], "Face ROI Crop", (825, 310))
    draw_path_with_arrow(draw, [(825, 460), (825, 520)], "512D Vector", (825, 490))

    # Nodes in Storage & Memory
    draw_box(draw, [1020, 200, 1240, 360], "In-Memory Gallery", ["Gallery.load_gallery()", "Scans Training Dataset", "Computes L2 Avg Vector", "Dict: {name: vector}"])
    draw_box(draw, [1020, 540, 1240, 700], "SQLite Database", ["attendance.db", "Table: attendance", "id, person_name", "date, time, status"])

    # Inter-tier Connections
    draw_path_with_arrow(draw, [(290, 370), (360, 370)], "POST /recognize", (325, 350))
    draw_path_with_arrow(draw, [(290, 670), (360, 510)], "GET /attendance", (325, 590))

    draw_path_with_arrow(draw, [(630, 215), (700, 215)], "Detect Face", (665, 195))
    draw_path_with_arrow(draw, [(630, 365), (700, 400)], "Extract Embed", (665, 385))

    draw_path_with_arrow(draw, [(1130, 360), (950, 580)], "Query Vectors", (1040, 470))
    draw_path_with_arrow(draw, [(630, 200), (1020, 240)], "Startup Build", (825, 140))

    draw_path_with_arrow(draw, [(630, 675), (1020, 620)], "SQL Queries", (825, 660))

    ensure_dir(filename)
    img.save(filename, "PNG")
    print(f"Saved {filename}")

# ==========================================
# 2. GENERATE RECOGNITION PIPELINE FLOWCHART
# ==========================================
def create_recognition_pipeline_png(filename):
    W, H = 1100, 1750
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Title
    t_text = "POST /recognize - FACE RECOGNITION & ATTENDANCE PIPELINE"
    tb = FONT_TITLE.getbbox(t_text)
    draw.text(((W - (tb[2] - tb[0])) / 2, 25), t_text, fill=TEXT_COLOR, font=FONT_TITLE)
    draw.line([(50, 65), (W - 50, 65)], fill=LINE_COLOR, width=2)
    
    cx = W / 2
    
    # Step 1: Start Node
    y = 90
    draw_ellipse_node(draw, [cx - 140, y, cx + 140, y + 50], "START: Client Uploads Image")
    
    # Arrow to Step 2
    draw_path_with_arrow(draw, [(cx, y + 50), (cx, y + 90)])
    y += 90
    
    # Step 2: Read & Decode Image
    draw_box(draw, [cx - 200, y, cx + 200, y + 70], "1. Read & Decode Image", ["Read bytes from UploadFile", "cv2.imdecode(np_buffer, IMREAD_COLOR)"])
    
    # Arrow to Step 3 (Decision 1: Valid Image?)
    draw_path_with_arrow(draw, [(cx, y + 70), (cx, y + 120)])
    y += 120
    
    # Step 3: Decision 1 - Image Valid?
    draw_diamond(draw, [cx - 150, y, cx + 150, y + 90], ["Valid Image", "Bytes & Matrix?"])
    
    # Decision 1 No branch -> Error Response
    draw_path_with_arrow(draw, [(cx + 150, y + 45), (cx + 340, y + 45), (cx + 340, y + 1600), (cx + 140, y + 1600)], "No", (cx + 240, y + 30))
    
    # Decision 1 Yes branch -> Step 4
    draw_path_with_arrow(draw, [(cx, y + 90), (cx, y + 140)], "Yes", (cx + 25, y + 115))
    y += 140
    
    # Step 4: SCRFD Face Detection
    draw_box(draw, [cx - 220, y, cx + 220, y + 75], "2. SCRFD Face Detection", ["Run models/scrfd_500m.onnx", "Filter detections by score >= 0.5"])

    # Arrow to Step 5 (Decision 2: Detected Face Count?)
    draw_path_with_arrow(draw, [(cx, y + 75), (cx, y + 120)])
    y += 120
    
    # Step 5: Decision 2 - Face Count?
    draw_diamond(draw, [cx - 160, y, cx + 160, y + 100], ["How Many Faces", "Detected?"])

    # Branch 0 faces
    draw_box(draw, [50, y + 140, 270, y + 220], "Response: No Face", ["recognized: false", "message: 'No face detected'"])
    draw_path_with_arrow(draw, [(cx - 160, y + 50), (160, y + 50), (160, y + 140)], "0 Faces", (cx - 240, y + 30))
    draw_path_with_arrow(draw, [(160, y + 220), (160, y + 1600), (cx - 140, y + 1600)])

    # Branch > 1 faces
    draw_box(draw, [W - 270, y + 140, W - 50, y + 220], "Response: Multi Faces", ["recognized: false", "message: 'Multiple faces'"])
    draw_path_with_arrow(draw, [(cx + 160, y + 50), (W - 160, y + 50), (W - 160, y + 140)], "> 1 Face", (cx + 240, y + 30))
    draw_path_with_arrow(draw, [(W - 160, y + 220), (W - 160, y + 1600), (cx + 140, y + 1600)])

    # Branch = 1 face -> Step 6
    draw_path_with_arrow(draw, [(cx, y + 100), (cx, y + 150)], "= 1 Face", (cx + 35, y + 125))
    y += 150

    # Step 6: Crop & Extract Embedding
    draw_box(draw, [cx - 220, y, cx + 220, y + 75], "3. Extract Facial Embedding", ["Crop detected face bounding box", "Run ArcFace MobileFaceNet -> 512D vector"])

    # Arrow to Step 7
    draw_path_with_arrow(draw, [(cx, y + 75), (cx, y + 120)])
    y += 120

    # Step 7: Gallery Cosine Similarity Search
    draw_box(draw, [cx - 240, y, cx + 240, y + 80], "4. Cosine Similarity Gallery Search", ["Compute similarity against cached embeddings", "Find highest similarity score S_max & identity"])

    # Arrow to Step 8 (Decision 3: S_max >= 0.5?)
    draw_path_with_arrow(draw, [(cx, y + 80), (cx, y + 130)])
    y += 130

    # Step 8: Decision 3 - Cosine Sim >= 0.5?
    draw_diamond(draw, [cx - 160, y, cx + 160, y + 100], ["Similarity Score", "S_max >= 0.5?"])

    # Decision 3 No branch -> Unknown Person Response
    draw_box(draw, [80, y + 140, 310, y + 220], "Response: Unknown", ["recognized: false", "message: 'Unknown person'"])
    draw_path_with_arrow(draw, [(cx - 160, y + 50), (195, y + 50), (195, y + 140)], "No (< 0.5)", (cx - 240, y + 30))
    draw_path_with_arrow(draw, [(195, y + 220), (195, y + 1600), (cx - 140, y + 1600)])

    # Decision 3 Yes branch -> Candidate Identified -> Step 9
    draw_path_with_arrow(draw, [(cx, y + 100), (cx, y + 150)], "Yes (>= 0.5)", (cx + 45, y + 125))
    y += 150

    # Step 9: Database Attendance Check
    draw_box(draw, [cx - 240, y, cx + 240, y + 75], "5. Attendance Duplicate Check", ["Query SQLite Attendance table for person & today's date"])

    # Arrow to Step 10 (Decision 4: Already Marked Today?)
    draw_path_with_arrow(draw, [(cx, y + 75), (cx, y + 120)])
    y += 120

    # Step 10: Decision 4 - Already Marked Today?
    draw_diamond(draw, [cx - 160, y, cx + 160, y + 100], ["Already Logged", "For Today?"])

    # Decision 4 Yes branch -> Already Marked Response
    draw_box(draw, [cx - 360, y + 140, cx - 80, y + 220], "Response: Already Marked", ["recognized: true, person: name", "message: 'Attendance already marked'"])
    draw_path_with_arrow(draw, [(cx - 160, y + 50), (cx - 220, y + 50), (cx - 220, y + 140)], "Yes", (cx - 190, y + 30))
    draw_path_with_arrow(draw, [(cx - 220, y + 220), (cx - 220, y + 310), (cx, y + 310)])

    # Decision 4 No branch -> Insert New Row -> Response: Marked
    draw_box(draw, [cx + 80, y + 140, cx + 360, y + 220], "Response: Marked New", ["Insert row (status='Present')", "recognized: true, person: name", "message: 'Attendance marked'"])
    draw_path_with_arrow(draw, [(cx + 160, y + 50), (cx + 220, y + 50), (cx + 220, y + 140)], "No", (cx + 190, y + 30))
    draw_path_with_arrow(draw, [(cx + 220, y + 220), (cx + 220, y + 310), (cx, y + 310)])

    # End Node
    y += 310
    draw_ellipse_node(draw, [cx - 140, y - 25, cx + 140, y + 25], "END: Return JSON")

    ensure_dir(filename)
    img.save(filename, "PNG")
    print(f"Saved {filename}")


# SVG Vector Generation
def create_system_architecture_svg(filename):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 850" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #ffffff; }
      .border { stroke: #000000; stroke-width: 2; fill: #ffffff; }
      .alt-bg { stroke: #000000; stroke-width: 2; fill: #f8f8f8; }
      .container { stroke: #000000; stroke-width: 1; fill: none; rx: 12; }
      .title { font-family: Arial, sans-serif; font-size: 24px; font-weight: bold; fill: #000000; text-anchor: middle; }
      .container-title { font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #000000; }
      .box-title { font-family: Arial, sans-serif; font-size: 17px; font-weight: bold; fill: #000000; text-anchor: middle; }
      .text-body { font-family: Arial, sans-serif; font-size: 14px; fill: #444444; text-anchor: middle; }
      .text-label { font-family: Arial, sans-serif; font-size: 13px; font-weight: bold; fill: #000000; text-anchor: middle; }
      .line { stroke: #000000; stroke-width: 2; fill: none; }
      .divider { stroke: #000000; stroke-width: 1; }
    </style>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#000000" />
    </marker>
  </defs>

  <rect class="bg" width="100%" height="100%" />

  <!-- Main Title -->
  <text x="650" y="45" class="title">FACE ATTENDANCE SYSTEM - SYSTEM ARCHITECTURE</text>
  <line x1="50" y1="65" x2="1250" y2="65" class="line" />

  <!-- Containers -->
  <rect x="40" y="90" width="270" height="690" class="container" />
  <text x="60" y="115" class="container-title">CLIENT TIER</text>

  <rect x="340" y="90" width="310" height="690" class="container" />
  <text x="360" y="115" class="container-title">FASTAPI BACKEND TIER</text>

  <rect x="680" y="90" width="290" height="690" class="container" />
  <text x="700" y="115" class="container-title">AI MODEL ENGINE</text>

  <rect x="1000" y="90" width="260" height="690" class="container" />
  <text x="1020" y="115" class="container-title">STORAGE &amp; MEMORY</text>

  <!-- Client Boxes -->
  <g transform="translate(60, 160)">
    <rect width="230" height="110" rx="10" class="border" />
    <text x="115" y="30" class="box-title">React Native App</text>
    <line x1="10" y1="42" x2="220" y2="42" class="divider" />
    <text x="115" y="62" class="text-body">Mobile UI (Expo)</text>
    <text x="115" y="82" class="text-body">Camera &amp; Server Config</text>
  </g>

  <g transform="translate(60, 320)">
    <rect width="230" height="100" rx="10" class="border" />
    <text x="115" y="30" class="box-title">HTTP API Client</text>
    <line x1="10" y1="42" x2="220" y2="42" class="divider" />
    <text x="115" y="62" class="text-body">multipart/form-data</text>
    <text x="115" y="82" class="text-body">Async fetch API</text>
  </g>

  <g transform="translate(60, 620)">
    <rect width="230" height="110" rx="10" class="border" />
    <text x="115" y="30" class="box-title">Attendance View</text>
    <line x1="10" y1="42" x2="220" y2="42" class="divider" />
    <text x="115" y="62" class="text-body">Displays History</text>
    <text x="115" y="82" class="text-body">Status Cards &amp; Alerts</text>
  </g>

  <path d="M 175 270 L 175 320" class="line" marker-end="url(#arrow)" />
  <path d="M 175 420 L 175 620" class="line" marker-end="url(#arrow)" />

  <!-- Backend Boxes -->
  <g transform="translate(360, 160)">
    <rect width="270" height="110" rx="10" class="border" />
    <text x="135" y="30" class="box-title">FastAPI App Router</text>
    <line x1="10" y1="42" x2="260" y2="42" class="divider" />
    <text x="135" y="62" class="text-body">backend/main.py</text>
    <text x="135" y="82" class="text-body">CORS &amp; Lifespan Startup</text>
  </g>

  <g transform="translate(360, 310)">
    <rect width="270" height="110" rx="10" class="border" />
    <text x="135" y="30" class="box-title">Recognition Route</text>
    <line x1="10" y1="42" x2="260" y2="42" class="divider" />
    <text x="135" y="62" class="text-body">POST /recognize</text>
    <text x="135" y="82" class="text-body">Orchestrate Pipeline</text>
  </g>

  <g transform="translate(360, 460)">
    <rect width="270" height="100" rx="10" class="border" />
    <text x="135" y="30" class="box-title">Attendance Route</text>
    <line x1="10" y1="42" x2="260" y2="42" class="divider" />
    <text x="135" y="62" class="text-body">POST / GET /attendance</text>
    <text x="135" y="82" class="text-body">Duplicate Prevention</text>
  </g>

  <g transform="translate(360, 620)">
    <rect width="270" height="110" rx="10" class="border" />
    <text x="135" y="30" class="box-title">SQLAlchemy Session</text>
    <line x1="10" y1="42" x2="260" y2="42" class="divider" />
    <text x="135" y="62" class="text-body">database.py (get_db)</text>
    <text x="135" y="82" class="text-body">SQLite Connection Engine</text>
  </g>

  <path d="M 495 270 L 495 310" class="line" marker-end="url(#arrow)" />
  <path d="M 495 420 L 495 460" class="line" marker-end="url(#arrow)" />
  <path d="M 495 560 L 495 620" class="line" marker-end="url(#arrow)" />

  <!-- AI Model Boxes -->
  <g transform="translate(700, 160)">
    <rect width="250" height="120" rx="10" class="border" />
    <text x="125" y="30" class="box-title">Face Detector (SCRFD)</text>
    <line x1="10" y1="42" x2="240" y2="42" class="divider" />
    <text x="125" y="62" class="text-body">scrfd_500m.onnx</text>
    <text x="125" y="82" class="text-body">Cutoff: 0.5 | 5 Landmarks</text>
    <text x="125" y="102" class="text-body">Crop &amp; Align Bounding Box</text>
  </g>

  <g transform="translate(700, 340)">
    <rect width="250" height="120" rx="10" class="border" />
    <text x="125" y="30" class="box-title">Face Recognizer</text>
    <line x1="10" y1="42" x2="240" y2="42" class="divider" />
    <text x="125" y="62" class="text-body">w600k_mbf.onnx</text>
    <text x="125" y="82" class="text-body">MobileFaceNet ArcFace</text>
    <text x="125" y="102" class="text-body">Generates 512D Vector</text>
  </g>

  <g transform="translate(700, 520)">
    <rect width="250" height="120" rx="10" class="border" />
    <text x="125" y="30" class="box-title">Cosine Matcher</text>
    <line x1="10" y1="42" x2="240" y2="42" class="divider" />
    <text x="125" y="62" class="text-body">Cosine Sim Threshold: 0.5</text>
    <text x="125" y="82" class="text-body">Finds Highest Match</text>
    <text x="125" y="102" class="text-body">Identifies Name</text>
  </g>

  <path d="M 825 280 L 825 340" class="line" marker-end="url(#arrow)" />
  <rect x="770" y="300" width="110" height="22" class="border" rx="4" />
  <text x="825" y="315" class="text-label">Face ROI Crop</text>

  <path d="M 825 460 L 825 520" class="line" marker-end="url(#arrow)" />
  <rect x="775" y="480" width="100" height="22" class="border" rx="4" />
  <text x="825" y="495" class="text-label">512D Vector</text>

  <!-- Storage Boxes -->
  <g transform="translate(1020, 200)">
    <rect width="220" height="160" rx="10" class="border" />
    <text x="110" y="30" class="box-title">In-Memory Gallery</text>
    <line x1="10" y1="42" x2="210" y2="42" class="divider" />
    <text x="110" y="65" class="text-body">Gallery.load_gallery()</text>
    <text x="110" y="85" class="text-body">Scans Train Dataset</text>
    <text x="110" y="105" class="text-body">Computes L2 Avg Vector</text>
    <text x="110" y="125" class="text-body">Dict: {name: vector}</text>
  </g>

  <g transform="translate(1020, 540)">
    <rect width="220" height="160" rx="10" class="border" />
    <text x="110" y="30" class="box-title">SQLite Database</text>
    <line x1="10" y1="42" x2="210" y2="42" class="divider" />
    <text x="110" y="65" class="text-body">attendance.db</text>
    <text x="110" y="85" class="text-body">Table: attendance</text>
    <text x="110" y="105" class="text-body">id, person_name</text>
    <text x="110" y="125" class="text-body">date, time, status</text>
  </g>

  <!-- Cross Connections -->
  <path d="M 290 370 L 360 370" class="line" marker-end="url(#arrow)" />
  <rect x="290" y="340" width="110" height="22" class="border" rx="4" />
  <text x="345" y="355" class="text-label">POST /recognize</text>

  <path d="M 290 670 L 360 510" class="line" marker-end="url(#arrow)" />
  <rect x="270" y="580" width="110" height="22" class="border" rx="4" />
  <text x="325" y="595" class="text-label">GET /attendance</text>

  <path d="M 630 215 L 700 215" class="line" marker-end="url(#arrow)" />
  <path d="M 630 365 L 700 400" class="line" marker-end="url(#arrow)" />

  <path d="M 1130 360 L 950 580" class="line" marker-end="url(#arrow)" />
  <path d="M 630 200 L 1020 240" class="line" marker-end="url(#arrow)" />
  <rect x="770" y="130" width="110" height="22" class="border" rx="4" />
  <text x="825" y="145" class="text-label">Startup Build</text>

  <path d="M 630 675 L 1020 620" class="line" marker-end="url(#arrow)" />
</svg>'''
    ensure_dir(filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {filename}")

if __name__ == "__main__":
    create_system_architecture_png("docs/images/system_architecture.png")
    create_recognition_pipeline_png("docs/images/recognition_pipeline.png")
    create_system_architecture_svg("docs/images/system_architecture.svg")
