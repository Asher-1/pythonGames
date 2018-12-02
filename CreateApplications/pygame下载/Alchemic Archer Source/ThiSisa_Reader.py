def Text2List(Text,Divider,intmode=False):
    List = []
    Current = ''
    for char in Text:
        if char != Divider:
            Current += char
        else:
            if intmode == True:
                try:
                    List.append(float(Current))
                except:
                    List.append(Current)
            else:
                List.append(Current)
            Current = ''
    return List

def load(mappath):
    file = open(mappath + '.txt','r')
    data = file.read()
    file.close()
    Word = ''
    num = 0
    rLayerData = ''
    for char in data:
        if (char != ' ') and (char != ':') and (char != '\n'):
            Word += char
        else:
            if Word == 'Tiles':
                rMapData = data[num:]
                rLayerData += '$'
            else:
                rLayerData += Word + char
            Word = ''
        num += 1
    rLayerData = rLayerData[7:]
    LayerData = ''
    MapData = rMapData
    for char in rLayerData:
        if char != '$':
            LayerData += char
        else:
            break
    LayerData = LayerData[1:]
    LayerData = Text2List(LayerData,'\n')
    NewLayerData = []
    for Layer in LayerData:
        NewLayerData.append(Text2List(Layer,';',True))
    LayerData = NewLayerData
    MapData = Text2List(MapData,'\n')
    NewMapData = []
    for Tile in MapData:
        NewMapData.append(Text2List(Tile,';',True))
    MapData = NewMapData
    return LayerData,MapData

def format_tiles(MapData,chunksize=200):
    TileChunks = {}
    for Tile in MapData:
        if Tile != []:
            ChunkX = int(Tile[2]/chunksize)
            ChunkY = int(Tile[3]/chunksize)
            if str(ChunkX) + ',' + str(ChunkY) not in TileChunks:
                TileChunks[str(ChunkX) + ',' + str(ChunkY)] = []
            TileChunks[str(ChunkX) + ',' + str(ChunkY)].append(Tile[:])
    return TileChunks
