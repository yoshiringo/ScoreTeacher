import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def Output_Graph():
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img = buffer.getvalue()
    graph = base64.b64encode(img)
    graph = graph.decode("utf-8")
    buffer.close()
    return graph

def Plot_PieChart(p,l):
    plt.rcParams['font.family'] = 'Hiragino Maru Gothic Pro'
    c = ["cyan", 'tomato', 'gold', 'lawngreen',"hotpink"]
    plt.switch_backend("AGG")
    plt.figure(figsize=(6,6))
    plt.pie(p, autopct="%d%%", labels = l, colors = c, counterclock=False, startangle=90, radius=1.2, center=(0, 0))
    
    graph = Output_Graph()
    return graph