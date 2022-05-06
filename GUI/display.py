import cv2
import os
import subprocess
from lineDetection import getLines
from filter import cropImage

def getWidthHeight(fileName):            
  width = 0
  height = 0
  with open(fileName) as svgFile:
      for svgStr in svgFile:
        if "width" in svgStr:
          widthIndex = svgStr.index("width=\"")
          widthStartIndex = widthIndex+7
          widthEndIndex = svgStr[widthStartIndex:].index("\"") + widthStartIndex
          width = svgStr[widthStartIndex:widthEndIndex]
          heightIndex = svgStr.index("height=\"")
          heightStartIndex = heightIndex+8
          heightEndIndex = svgStr[heightStartIndex:].index("\"") + heightStartIndex
          height = svgStr[heightStartIndex:heightEndIndex]
          break 
  return float(width), float(height)


# [[(1, 2), (3, 4)]]
def display(graph, lineList, output_path, graph_width, graph_height, graphedLines, figureIndex):
  width, height = getWidthHeight(output_path)
  widthProp = (float) (graph_width/width)
  heightProp = (float) (graph_height/height)

  #graphedLines = {}
  lastFig = -1
  for line in lineList:
    x0, y0 = line[0]
    x1, y1 = line[1]
    adjustedx0 = x0 * widthProp
    adjustedy0 = graph_height - y0 * heightProp
    adjustedx1 = x1 * widthProp
    adjustedy1 = graph_height - y1 * heightProp
    graph.draw_line((adjustedx0 , adjustedy0), (adjustedx1, adjustedy1), width=4)

    drag_figures = graph.get_figures_at_location((adjustedx0,adjustedy0))
    lastFig = -1
    for fig in drag_figures:
      if fig not in graphedLines:
        #print("GRAPHED LINES FOR FIGURE ", fig, ": ")
        #print(graphedLines)
        graphedLines[fig] = [(adjustedx0 , adjustedy0), (adjustedx1, adjustedy1)]
        lastFig = fig
  
  figureIndex = lastFig + 1
  return graphedLines, figureIndex

def groupLines(graph, x, y, graphedLines, figureIndex):
  drag_figures = graph.get_figures_at_location((x,y))
  minX = None
  minY = None
  maxX = None
  maxY = None
  delete = []
  for fig in drag_figures:  
      (endpoint0, endpoint1) = graphedLines[fig]
      x0 = endpoint0[0]
      y0 = endpoint0[1]
      x1 = endpoint1[0]
      y1 = endpoint1[1]
      if minX == None:
          minX = min(x0, x1)
          minY = min(y0, y1)

          maxX = max(x0, x1)
          maxY = max(y0, y1)
      else:
          minx0 = min(x0, x1)
          miny0 = min(y0, y1)
          maxx1 = max(x0, x1)
          maxy1 = max(y0, y1)

          minX = min(minx0, minX)
          minY = min(miny0, minY)

          maxX = max(maxx1, maxX)
          maxY = max(maxy1, maxY)
      delete.append(fig)
  
  for delFig in delete:
      graph.delete_figure(delFig)
      #print("deleting figure ", delFig)
      graphedLines.pop(delFig)

  if minX != None:
      graph.draw_line((minX , minY), (maxX, maxY), width=4, color = "red")
      #print("adding figure ", figureIndex)
      graphedLines[figureIndex] = [(minX , minY), (maxX, maxY)]
      figureIndex += 1
      #print("graphedLines: ", graphedLines)
      #print("------------------------")

  return graphedLines, figureIndex


def vectorize(frame, file_name):
    path = os.getcwd()
    base_path = path[:-3] + "vectorization/images"
    base_path1 = path[:-3] + "vectorization/results"
    input_path = os.path.join(base_path , file_name +'.jpg')
    output_path = os.path.join(base_path1 , file_name+'.svg')
    convert = subprocess.run("vtracer --input " + input_path + " --output " + output_path, shell =True)


def vectorizeImage(frame, graph, graph_size, graphedLines, figureIndex):
  file_name =  'frame'

  path = os.getcwd()
  base_path = path[:-3] + "vectorization/images"
  input_path = os.path.join(base_path , file_name + '.jpg')
  cv2.imwrite(input_path[:-5]+'.jpg', frame)
  result = cropImage(input_path[:-5]+'.jpg')
  cv2.imwrite(input_path, result)

    # get lines using computer vision
  line_file_name, paths = getLines(file_name)
  
  # can delete below line after testing
  image_to_vectorize = cv2.imread(os.path.join(base_path , line_file_name + '.jpg'))

  vectorize(image_to_vectorize, line_file_name)
  base_path1 = os.getcwd()[:-3] + "vectorization/results"
  output_path = os.path.join(base_path1 , line_file_name+'.svg')

  graphedLines, figureIndex = display(graph, paths, output_path, graph_size[0], graph_size[1], graphedLines, figureIndex)
  #figureIndex = len(graphedLines) + 1

  return graphedLines, figureIndex


def addGraphLines(graph, graphedLines, receivedGraphedLines, figureIndex):

  if (len(graphedLines.keys()) > 0):
    maxOriginalKey = max(graphedLines.keys())
  else:
    if (len(receivedGraphedLines.keys()) == 0):
      return graphedLines, figureIndex
    maxOriginalKey = max(receivedGraphedLines)

  if (figureIndex == None):
    figureIndex = -1
  #newFigureIndex = figureIndex + 1

  for fig in receivedGraphedLines.keys():
    (endpoint0, endpoint1) = receivedGraphedLines[fig]
    x0 = endpoint0[0]
    y0 = endpoint0[1]
    x1 = endpoint1[0]
    y1 = endpoint1[1]
    
    newline = graph.draw_line((x0 , y0), (x1, y1), width=4)
    if newline not in graphedLines:
      #print("GRAPHED LINES FOR FIGURE ", fig, ": ")
      #print(graphedLines)
      graphedLines[newline] = [(x0 , y0), (x1, y1)]
      lastFig = newline
  
  figureIndex = newline + 1

    

  return graphedLines, figureIndex
