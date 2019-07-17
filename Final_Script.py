
# coding: utf-8

# In[64]:


import sys
import os
import math
import qahirah as qah
from qahirah import     CAIRO,     Colour,     Glyph,     Vector
ft = qah.get_ft_lib()
import fribidi as fb
from fribidi import     FRIBIDI as FB
import harfbuzz as hb
import numpy as np
import pickle
from PIL import Image
from array import array
import pickle
import io

# In[65]:


f = open('temp.pkl','rb')
di = pickle.load(f)

def pngB_to_np(pngB) :
    return np.array(Image.open(io.BytesIO(pngB)))

# In[66]:


# To get the bound of the glyph
def get_Bound_Glyph(abc):
    
    # Setting Starting position of the first glyph
    glyph_pos = Vector(0,0)
    
    # Resetting the buffer
    buf.reset()
    
    # adding string to buffer
    buf.add_str(abc)
    
    # Figuring out segmentation properties
    buf.guess_segment_properties()
    
    # Gernerating Shapes for the text in buffer using the font
    hb.shape(hb_font, buf)
    
    # Getting glyphs out of buffer (list format)
    glyphs, end_glyph_pos = buf.get_glyphs(glyph_pos)
    
    # Creating fontface 
    qah_face = qah.FontFace.create_for_ft_face(ft_face)

    
    glyph_extents =         (qah.Context.create_for_dummy()
            .set_font_face(qah_face)
            .set_font_size(text_size)
            .glyph_extents(glyphs)
        )
    
    # Getting the bound of the [glyphs]
    figure_bounds = math.ceil(glyph_extents.bounds)
    
    # Returning glyph and the figure bound
    return (figure_bounds,glyphs)

# def get_glyphs(abc):
#     glyphs = []
#     glyph_pos = Vector(0,0)
#     buf.reset()
#     buf.add_str(abc)
#     buf.guess_segment_properties()
#     hb.shape(hb_font, buf)
#     new_glyphs, end_glyph_pos = buf.get_glyphs(glyph_pos)
#     glyphs.extend(new_glyphs)
#     #print(new_glyphs)
#     qah_face = qah.FontFace.create_for_ft_face(ft_face)

#     glyph_extents = \
#         (qah.Context.create_for_dummy()
#             .set_font_face(qah_face)
#             .set_font_size(text_size)
#             .glyph_extents(glyphs)
#         )
#     return glyphs


# In[67]:


#di.keys()


# In[68]:


spaceWidth = di['space']
surfx,surfy = di['surf_dim']
font_path = di['font']
font_size = di['font_size']

lines = di['lines']
fsize = Vector(int(surfx),int(surfy))
line_spacing = di['line_spacing']


# In[69]:



# Creating Surface
pix = qah.ImageSurface.create   (
    format = CAIRO.FORMAT_RGB24,
    dimensions = fsize
  )


# In[70]:


# Creating ft_face
ft_face = ft.new_face(font_path)
text_size = font_size
# Creating Buffer
buf = hb.Buffer.create()
# setting char size to font face
ft_face.set_char_size(size = text_size, resolution = qah.base_dpi)
hb_font = hb.Font.ft_create(ft_face)
qah_face = qah.FontFace.create_for_ft_face(ft_face)


# In[71]:


ctx = qah.Context.create(pix)
# ctx.set_source_colour(Colour.grey(0))
# ctx.paint()
ctx.set_source_colour(Colour.grey(1))
ctx.set_font_face(qah_face)
ctx.set_font_size(text_size)


# In[72]:

factor = 0 
y = 0
bb = []
for l in lines:
            l = l.split()
            l = " ".join(l)
            x = 0 # carriage-return
            y += line_spacing # line-feed
            
            prev_tot_wid = 1000
            st = ''
            ln = len(l)
            i = 0
            bbCount = 0
            charLen = 0
            diffCount = 0
            for ch in l: # render each character
                if ch.isspace(): # just shift
                    st_bound,glyph3 = get_Bound_Glyph(st)
                    shift = (st_bound.topleft)[0]
                    
                    bb.append(np.array([x+shift,y+(st_bound.topleft)[1],st_bound.width,st_bound.height]))
                    bbCount += 1

                    ctx.translate(Vector(x+shift,y))
                    ctx.set_source_colour(Colour.grey(1))
                    ctx.set_font_face(qah_face)
                    ctx.set_font_size(text_size)
                    ctx.show_glyphs(glyph3)
                    # ctx.glyph_path(glyph3)
                    # ctx.stroke()
                    ctx.translate(Vector(-(x+shift),-y))
                    
                    diffCount = charLen - bbCount

                    for faltuItr in range(diffCount):
                        bb.append(np.array([x+shift,y+(st_bound.topleft)[1],st_bound.width,st_bound.height]))

                    bbCount = 0
                    charLen = 0

                    x+= st_bound.width+shift
                    
                    x += spaceWidth
                    st = ''
                    prev_tot_wid = 1000
                    
                else:
                    charLen += 1
                    curr_bound,glyph1 = get_Bound_Glyph(ch)
                    if i == 0:
                        factor = curr_bound.width/3
                    upto_bound,glyph2 = get_Bound_Glyph(st+ch)
                    if (upto_bound.width)+factor < prev_tot_wid+curr_bound.width: #
                        st = st + ch
                        prev_tot_wid = upto_bound.width
                    else:
                        st_bound,glyph3 = get_Bound_Glyph(st)
                        shift = (st_bound.topleft)[0]
                        bb.append(np.array([x+shift,y+(st_bound.topleft)[1],st_bound.width,st_bound.height]))
                        bbCount += 1

                        ctx.translate(Vector(x+shift,y))
                        ctx.set_source_colour(Colour.grey(1))
                        ctx.set_font_face(qah_face)
                        ctx.set_font_size(text_size)
                        ctx.show_glyphs(glyph3)
                        # ctx.glyph_path(glyph3)
                        # ctx.stroke()
                        ctx.translate(Vector(-(x+shift),-y))
                        x+= st_bound.width+shift
                        st = ch
                        prev_tot_wid = curr_bound.width
                    
                    if i == ln-1:
                        # shift = (st_bound.topleft)[0]
                        st_bound,gly5 = get_Bound_Glyph(st)
                        shift = (st_bound.topleft)[0]

                        ctx.translate(Vector(x+shift,y))
                        # ctx.set_source_colour(Colour.grey(0))
                        # ctx.paint()
                        #glyphs = get_glyphs(st)
                        ctx.set_source_colour(Colour.grey(1))
                        ctx.set_font_face(qah_face)
                        ctx.set_font_size(text_size)
                        ctx.show_glyphs(gly5)
                        # ctx.glyph_path(gly5)
                        # ctx.stroke()
                        ctx.translate(Vector(-(x+shift),-y))
                        bb.append(np.array([x+shift,y+(st_bound.topleft)[1],st_bound.width,st_bound.height]))
                        bbCount += 1

                        diffCount = charLen - bbCount

                        for fitr in range(diffCount):
                            bb.append(np.array([x+shift,y+(st_bound.topleft)[1],st_bound.width,st_bound.height]))

                        charLen = 0
                        bbCount = 0
                i += 1
               
                    
                    

                    
                    
                    
                    
                    
#                     # render the character
#                     ch_bounds = font.render_to(surf, (x,y), ch)
#                     ch_bounds.x = x + ch_bounds.x
#                     ch_bounds.y = y - ch_bounds.y
#                     x += ch_bounds.width
#                     bbs.append(np.array(ch_bounds))


img = pngB_to_np(pix.to_png_bytes())

dicc= {}
dicc['img'] = img[:,:,1]
dicc['bb'] = bb

pl = open('temp2.pkl','wb')
pickle.dump(dicc,pl,protocol=2)
pl.close()



