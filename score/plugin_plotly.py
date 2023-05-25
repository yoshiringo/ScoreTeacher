import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import matplotlib.font_manager as fm

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
    #デプロイ用
    
    font_path = "/usr/share/fonts/ipa-gothic/ipag.ttf"
    font = fm.FontProperties(fname=font_path, size=14)
    c = ["cyan", 'tomato', 'gold', 'lawngreen',"hotpink", "lavenderblush"]
    plt.switch_backend("AGG")
    plt.figure(figsize=(6,6))
    plt.pie(p, autopct="%d%%", labels = l, colors = c, counterclock=False, startangle=90, radius=1.0, center=(0, 0), pctdistance=0.7, textprops={'fontproperties': font})
    plt.subplots_adjust(left=0.2)
    
    """
    #ローカル用
    plt.rcParams['font.family'] = 'Hiragino Maru Gothic Pro'
    c = ["cyan", 'tomato', 'gold', 'lawngreen',"hotpink", "lavenderblush"]
    plt.switch_backend("AGG")
    plt.figure(figsize=(6,6))
    plt.pie(p, autopct="%d%%", labels = l, colors = c, counterclock=False, startangle=90, radius=1.0, center=(0, 0), pctdistance=0.7)
    plt.subplots_adjust(left=0.2)
    """

    graph = Output_Graph()
    return graph
    