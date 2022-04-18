

  
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
          print("width:" + width)
          heightIndex = svgStr.index("height=\"")
          heightStartIndex = heightIndex+8
          heightEndIndex = svgStr[heightStartIndex:].index("\"") + heightStartIndex
          height = svgStr[heightStartIndex:heightEndIndex]
          print("height:" + height)
          break 
  return float(width), float(height)


# [[(1, 2), (3, 4)]]
def display(graph, lineList, output_path, graph_width, graph_height):
  width, height = getWidthHeight(output_path)
  widthProp = (float) (graph_width/width)
  heightProp = (float) (graph_height/height)
  for line in lineList:
    x0, y0 = line[0]
    x1, y1 = line[1]
    #print("original: ", x0, y0, x1, y1)
    #print("after: ", x0 * widthProp, y0 * heightProp, x1 * widthProp , y1 * heightProp)
    # display_line()
    graph.draw_line((x0 * widthProp , graph_height - y0 * heightProp), (x1 * widthProp, graph_height - y1 * heightProp), width=4)





