from OpenGL.GL import *

from PIL import Image
#https://learnopengl.com/Getting-started/Textures
class Texture:
    def __init__(self, fdir):
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture) # all upcoming GL_TEXTURE_2D operations now have effect on this texture object
        # set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)    # set texture wrapping to GL_REPEAT (default wrapping method)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # load image, create texture and generate mipmaps
        try:
            img = Image.open(fdir)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())
            glGenerateMipmap(GL_TEXTURE_2D)

            img.close()
        except:
            print("Failed to load texture")
        self.texture = texture

    def update(self, data):
        1
    
    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)

#update texture
#live stream texture.