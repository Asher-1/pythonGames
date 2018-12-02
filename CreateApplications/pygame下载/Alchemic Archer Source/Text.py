import pygame
def GenerateFont(FontImage,FontSpacing,TileSize):
    FontOrder = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','.','-',',',':','+','\'','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','!','?','0','1','2','3','4','5','6','7','8','9']
    FontImage = pygame.image.load(FontImage).convert()
    FontImage.set_colorkey((255,255,255))
    num = 0
    for char in FontOrder:
        FontImage.set_clip(pygame.Rect(((TileSize+1)*num),0,TileSize,TileSize))
        CharacterImage = FontImage.subsurface(FontImage.get_clip())
        FontSpacing[char].append(CharacterImage)
        num += 1
    FontSpacing['Height'] = TileSize
    return FontSpacing
def ShowText(Text,X,Y,Spacing,WidthLimit,Font,surf):
    OriginalX = X
    OriginalY = Y
    CurrentWord = ''
    for char in Text:
        if char not in [' ','\n']:
            try:
                Image = Font[str(char)][1]
                CurrentWord += str(char)
            except KeyError:
                pass
        else:
            WordTotal = 0
            for char2 in CurrentWord:
                WordTotal += Font[char2][0]
                WordTotal += Spacing
            if WordTotal+X-OriginalX > WidthLimit:
                X = OriginalX
                Y += Font['Height']
            for char2 in CurrentWord:
                Image = Font[str(char2)][1]
                surf.blit(Image,(X,Y))
                X += Font[char2][0]
                X += Spacing
            if char == ' ':
                X += Font['A'][0]
                X += Spacing
            else:
                X = OriginalX
                Y += Font['Height']
            CurrentWord = ''
        if X-OriginalX > WidthLimit:
            X = OriginalX
            Y += Font['Height']
    return X,Y
