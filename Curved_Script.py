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
from matplotlib import pyplot as plt

from qahirah import cairo
import io
from PIL import Image
from array import array
import pickle

f = open('tmp_curved.pkl','rb')
d = pickle.load(f)
# In[635]:


## To convert PNG ByteStream Data into Image
def pngB_to_np(pngB) :
    return np.array(Image.open(io.BytesIO(pngB)))


# In[636]:


## To convert Degree in the Radian
def to_rad(degree):
    return (degree/360)*2*(np.pi)

# BaseLine Class from Ankush Gupta's Code
class BaselineState(object):
    curve = lambda this, a: lambda x: a*x*x
    differential = lambda this, a: lambda x: 2*a*x
    a = [0.50, 0.05]

    def get_sample(self):
        """
        Returns the functions for the curve and differential for a and b
        """
        sgn = 1.0
        if np.random.rand() < 0.5:
            sgn = -1

        a = self.a[1]*np.random.randn() + sgn*self.a[0]
        return {
            'curve': self.curve(a),
            'diff': self.differential(a),
        }


# In[637]:


## Code to get Rect
def get_rect(glyphs,angle=0):
    angle = to_rad(angle)
    ctx = qah.Context.create_for_dummy()
    ctx.set_font_face(qah_face)
    ctx.set_font_size(text_size)
    ctx.rotate(angle)
    b = ctx.glyph_extents(glyphs)
    b.y_bearing = b.y_bearing*(-1)
    return b.bounds


# In[638]:


# Code to get bound of a character in case it rotated
def boundB(imm): 
    (sx,sy) = imm.shape
    first = 0
    for i in range (sy):
        if np.sum(imm[:,i] != 0) and first == 0 :
            leftx = i
            first = 1

        if first == 1 and np.sum(imm[:,i] != 0)==0:
            rightx = i-1
            break

    fchck = 0
    for i in range(sx):
        if np.sum(imm[i,:] !=0) and fchck == 0:
            top = i 
            fchck = 1
        if fchck ==1 and np.sum(imm[i,:] != 0) == 0:
            bottom = i-1
            break
    
    return (leftx,top,rightx-leftx+1,bottom-top+1)


# In[639]:


# To get glyph and bounds of a glyphs
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

    
    glyph_extents = (qah.Context.create_for_dummy()
            .set_font_face(qah_face)
            .set_font_size(text_size)
            .glyph_extents(glyphs)
        )
    
    # Getting the bound of the [glyphs]
    figure_bounds = math.ceil(glyph_extents.bounds)
    
    # Returning glyph and the figure bound
    return (figure_bounds,glyphs)


# In[640]:



## To get artificial bounding box. 
## Sort of create a new surface plot character and then search starting and ending co-ordinate
def art_BB(ch,x,y,rot):
    #     creating new surface here
    surf = qah.ImageSurface.create(
    format = CAIRO.FORMAT_RGB24,
    dimensions = fsize
    )
    cnt = qah.Context.create(surf)
    cnt.translate(Vector(x,y))
    cnt.rotate(rot)
    cnt.set_source_colour(Colour.grey(1))
    cnt.set_font_face(qah_face)
    cnt.set_font_size(text_size)
    cnt.show_glyphs(ch)
    cnt.glyph_path(ch)
    cnt.stroke()
    img = pngB_to_np(surf.to_png_bytes())
    bb = boundB(img[:,:,1])
    # plt.imshow(img[:,:,1])
    return bb


# In[641]:


## Our implementation of python library to_render function which is used to render character on surface
## Beware our code only work with glyphs not character
def to_render(rect, ch, rot=0):
    rot = to_rad(rot)
    rot = (-1)*rot
    x = rect[0]
    y = rect[1]
    try:
        ctx.translate(Vector(x,y))
        ctx.rotate(rot)
        ctx.set_source_colour(Colour.grey(1))
        ctx.set_font_face(qah_face)
        ctx.set_font_size(text_size)
        ctx.show_glyphs(ch)
        # ctx.glyph_path(ch)
        # ctx.stroke()
        ctx.rotate(-rot)
        ctx.translate(Vector(-x,-y))

    except:
        ef = open('errorFile.txt','a')
        st = 'X co-ordinate ' + str(x) + ', Y co-ordinate ' + str(y) + ', Angle ' + str(rot)
        ef.write(st)
        ef.close()
    
    return art_BB(ch,x,y,rot)


# In[660]:


## To get the glyphlist
def glyphList(l):
    y = 0
    glyph_list = []

    x = 0 # carriage-return
    y += line_spacing # line-feed

    prev_tot_wid = 1000
    st = ''
    ln = len(l)
    i = 0
    for ch in l: # render each character
        curr_bound,glyph1 = get_Bound_Glyph(ch)
        if i == 0:
            factor = curr_bound.width/3
        upto_bound,glyph2 = get_Bound_Glyph(st+ch)
        if upto_bound.width+factor < prev_tot_wid+curr_bound.width: #
            st = st + ch
            prev_tot_wid = upto_bound.width

        else:
            st_bound,glyph3 = get_Bound_Glyph(st)
            glyph_list.append(glyph3)
            st = ch
            prev_tot_wid = curr_bound.width


        if i == ln-1:
            st_bound,gly5 = get_Bound_Glyph(st)
            glyph_list.append(gly5)
        i += 1

    return glyph_list


# In[661]:


# font_size = 25.53125
# fsize = Vector(170, 108)
# line_spacing = 43
# spaceWidth = 24
# surfx,surfy = (1000, 500)
# font_path = '/home/jaya/sp/SynthText/data/fonts/ubuntu/NotoSans-Regular.ttf'
# # font_size = font_size

# l = u'चिन्नास्वामी'


# In[662]:

# spaceWidth = di['space']
# surfx,surfy = di['surf_dim']
# font_path = di['font']
# font_size = di['font_size']

# lines = di['lines']
# fsize = Vector(int(surfx),int(surfy))
# line_spacing = di['line_spacing']

# spaceWidth = d['space']
# surfx,surfy = d['surf_dim']
font_path = d['font']
font_size = d['font_size']
l = d['word_text']
# lines = d['lines']
fsize = d['fsize']
line_spacing = d['line_spacing']
fsize = Vector(int(fsize[0]),int(fsize[1]))




pix = qah.ImageSurface.create   (
    format = CAIRO.FORMAT_RGB24,
    dimensions = fsize

  )


# In[663]:


# Creating ft_face
ft_face = ft.new_face(font_path)
text_size = font_size
# Creating Buffer
buf = hb.Buffer.create()
# setting char size to font face
ft_face.set_char_size(size = text_size, resolution = qah.base_dpi)
hb_font = hb.Font.ft_create(ft_face)
qah_face = qah.FontFace.create_for_ft_face(ft_face)

ctx = qah.Context.create(pix)
ctx.set_source_colour(Colour.grey(0))
ctx.paint()
# ctx.set_source_colour(Colour.grey(1))
# ctx.set_font_face(qah_face)
# ctx.set_font_size(text_size)


# In[664]:

l = l.strip()
actual_len  = len(l)
word_text = glyphList(l)
wl = len(word_text)

# actual_len,wl


# In[665]:


mid_idx = wl//2
bsln = BaselineState()
BS = bsln.get_sample()
curve = [BS['curve'](i-mid_idx) for i in range(wl)]
# some changes 
if wl <= 1:
    curve[mid_idx] = 0
else:
    curve[mid_idx] =  -(np.sum(curve)/(wl-1))


# In[666]:


rots  = [-int(math.degrees(math.atan(BS['diff'](i-mid_idx)/(font_size/2)))) for i in range(wl)]


# In[667]:


# /rots


# In[668]:


rect = get_rect(word_text[mid_idx])


# In[669]:


leftx = pix.width/2 - rect.width/2
topx = pix.height/2 +rect.height/2 +curve[mid_idx]
rect2 = (leftx,topx)
rect.top = topx
rect.left = leftx
(rect.left,rect.top)


# In[670]:





# In[671]:


mid_b = to_render(rect2, word_text[mid_idx],rots[mid_idx])
mid_bbs = np.array(mid_b)


# In[672]:


last_rect = rect


# In[673]:

bbs = []
ch_idx = []
for i in range(wl):
    if i == mid_idx:
        bbs.append(mid_bbs)
        ch_idx.append(i)
        continue
        
    if i < mid_idx: #left-chars
        i = mid_idx-1-i
    elif i==mid_idx+1: #right-chars begin
        last_rect = rect
        
        
    ch_idx.append(i)
    ch = word_text[i]

    newrect = get_rect(ch)
    newrect.top = last_rect.top
    
    if i > mid_idx:
        (newrect.left,newrect.top) = (last_rect.topleft[0]+last_rect.width+2, newrect.topleft[1])
    else:
        (newrect.left,newrect.top) = (last_rect.topleft[0]-2-newrect.width, newrect.topleft[1])
    newrect.top = max(newrect.height, min(fsize[1] - newrect.height, newrect.middle[1] + curve[i])) - newrect.height/2 
    try:
        bbrect = to_render((newrect.left,newrect.top),ch,rots[i])
    except ValueError:
        bbrect = to_render((newrect.left,newrect.top), ch,0)
    bbs.append(np.array(bbrect))
    last_rect = newrect

bbs_sequence_order = []

bbs_sequence_order = [None for i in ch_idx]

for idx,i in enumerate(ch_idx):
    bbs_sequence_order[i] = bbs[idx]
bbs = bbs_sequence_order

diffCount = actual_len - wl

bblast = bbs[wl-1]

for faltuItr in range(diffCount):
    bbs.append(np.array([bblast[0]+bblast[2],bblast[1],0,bblast[3]]))
    
    

# pix.flush().write_to_png('spcurved.png')
img = pngB_to_np(pix.to_png_bytes())

dicc= {}
dicc['img'] = img[:,:,1]
dicc['bb'] = bbs

pl = open('save_curve.pkl','wb')
# print("saved")
pickle.dump(dicc,pl,protocol=2)
pl.close()


