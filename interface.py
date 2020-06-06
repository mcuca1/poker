# sample_one.py

import os
import wx
import math
from wx import svg
import svgutils
import wx.lib.inspection
try:
	import wx.lib.wxcairo as wxcairo
	import cairo
	haveCairo = True
except ImportError:
	haveCairo = False

# def opj
# class MyPanel
# class MyFrame
# class MyApp

def angles_in_ellipse(num, b ,a):
	import numpy as np
	import scipy as sp
	import scipy.optimize
	from math import pi
	assert(num > 0)
	assert(a < b)
	print(num, a, b)
	angles = 2 * np.pi * np.arange(num) / num
	if a != b:
		e = (1.0 - a ** 2.0 / b ** 2.0) ** 0.5
		tot_size = sp.special.ellipeinc(2.0 * np.pi, e)
		arc_size = tot_size / num
		arcs = np.arange(num) * arc_size
		res = sp.optimize.root(
			lambda x: (sp.special.ellipeinc(x, e) - arcs), angles)
		angles = res.x
	angles = [angle*180/pi+90 for angle in angles]
	print(angles)
	return angles
def point_on_circle(center, radius, angle, xscale, yscale):
	'''
		Finding the x,y coordinates on circle, based on given angle
	'''
	from math import cos, sin, pi
	#center of circle, angle in degree and radius of circle
	x = center[0] + (radius*xscale * cos(angle*pi/180))
	y = center[1] + (radius*yscale * sin(angle*pi/180))

	return x,y


def GetCardFromFile(card, rotation):
	cards_root = r'C:\Users\marco\Documents\GitHub\poker\cards'
	card_path = os.path.join(cards_root, card + ".svg")
	print(card_path)
	svg = svgutils.transform.fromfile(card_path)
	originalSVG = svgutils.compose.SVG(card_path)
	originalSVG.rotate(rotation, int(svg.height)/2, int(svg.width)/2)
	if rotation >= 0: 
		originalSVG.move(50,50)
	else:
		originalSVG.move(50,40)
	figure = svgutils.compose.Figure(svg.height, svg.width, originalSVG)
	figure_bytes = figure.tostr()
	svg_image = wx.svg.SVGimage.CreateFromBytes(figure_bytes)
	return svg_image


#----------------------------------------------------------------------

def opj(path):
	"""
	Convert paths to the platform-specific separator.
	"""

	st = os.path.join(*tuple(path.split('/')))
	# HACK: on Linux, a leading / gets lost...
	if path.startswith('/'):
		st = '/' + st
	return st

#----------------------------------------------------------------------

class MyPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)

		self.card1 = GetCardFromFile("AH", -3)
		self.card2 = GetCardFromFile("KD", 2)

	def OnSize(self,event):
		print("resize")
		self.Refresh()

	def OnPaint(self, evt):
		"""
		...
		"""

		if self.IsDoubleBuffered():
			dc = wx.PaintDC(self)
		else:
			dc = wx.BufferedPaintDC(self)
		dc.SetBackground(wx.BLACK_BRUSH)
		dc.Clear()

		self.Render(dc)

	def DrawPlayers(self, n_players, table_size, ctx, xscale, yscale):
		# ctx.scale(0.95, 1)
		ellipse_a = table_size * xscale
		ellipse_b = table_size * yscale
		angles = angles_in_ellipse(n_players, ellipse_a ,ellipse_b)
		player_size = 30
		offset = 27
		sz = self.GetSize()
		xc = sz[0]/2
		yc = sz[1]/2
		frame_scale = sz[0] / 640
		for angle in angles:
			ctx.set_line_width(1)
			x, y = point_on_circle([xc, yc], table_size*frame_scale, angle, xscale, yscale)
			ctx.set_line_width(1)
			ctx.arc(x, y-offset*frame_scale, player_size*frame_scale, 0, math.pi*2)
			ctx.set_source_rgba(72/255, 71/255, 102/255, 0.9)
			ctx.fill_preserve()
			ctx.set_source_rgb(168, 158, 158)
			ctx.stroke()
			card_size = 0.165
			bitmap1 = self.card1.ConvertToBitmap(scale=card_size*frame_scale, width=self.card1.width, height=self.card1.height)
			bitmap2 = self.card2.ConvertToBitmap(scale=card_size*frame_scale, width=self.card2.width, height=self.card2.height)
			surface1 = wxcairo.ImageSurfaceFromBitmap(bitmap1)
			surface2 = wxcairo.ImageSurfaceFromBitmap(bitmap2)
			ctx.set_source_surface(surface1, x-(player_size*frame_scale), y-(offset*2*frame_scale))
			ctx.paint()
			ctx.set_source_surface(surface2, x-(player_size/2*frame_scale), y-(offset*2*frame_scale))
			ctx.paint()

		

	def Render(self, dc):
		"""
		...
		"""

		# # Draw some stuff on the plain dc.
		sz = self.GetSize()
		xc = sz[0]/2
		yc = sz[1]/2
		frame_scale = sz[0] / 640
		# dc.SetPen(wx.Pen("navy", 1))

		# x = y = 0
		# while x < sz.width * 2 or y < sz.height * 2:
		# 	x += 20
		# 	y += 20
		# 	dc.DrawLine(x, 0, 0, y)

		# # Now draw something with cairo.
		ctx = wxcairo.ContextFromDC(dc)
		# ctx.set_line_width(15)
		# ctx.move_to(125, 25)
		# ctx.line_to(225, 225)
		# ctx.rel_line_to(-200, 0)
		# ctx.close_path()
		# ctx.set_source_rgba(0, 0, 0.5, 1)
		# ctx.stroke()

		# And something else...
		ctx.save()
		factor = 2
		table_size = 130
		ctx.scale(factor, 1)
		ctx.arc(xc/factor, yc, table_size*frame_scale, 0, math.pi*2)
		ctx.set_source_rgba(58/255, 121/255, 85/255, 1)
		ctx.fill_preserve()
		ctx.scale(1, 0.5)
		ctx.set_source_rgb(1, 0.5, 0)
		ctx.stroke()
		ctx.restore()

		self.DrawPlayers(6, table_size, ctx, 2, 1)

		# # Here's a gradient pattern.
		# ptn = cairo.RadialGradient(315, 70, 25,
		# 						   302, 70, 128)
		# ptn.add_color_stop_rgba(0, 1,1,1,1)
		# ptn.add_color_stop_rgba(1, 0,0,0,1)
		# ctx.set_source(ptn)
		# ctx.arc(328, 96, 75, 0, math.pi*2)
		# ctx.fill()

		# # Draw some text.
		# face = wxcairo.FontFaceFromFont(
		# 	wx.FFont(10, wx.FONTFAMILY_SWISS, wx.FONTFLAG_BOLD))
		# ctx.set_font_face(face)
		# ctx.set_font_size(60)
		# ctx.move_to(360, 180)
		# ctx.set_source_rgb(0, 0, 0)
		# ctx.show_text("Hello")

		# # Text as a path, with fill and stroke.
		# ctx.move_to(400, 220)
		# ctx.text_path("World")
		# ctx.set_source_rgb(0.39, 0.07, 0.78)
		# ctx.fill_preserve()
		# ctx.set_source_rgb(0,0,0)
		# ctx.set_line_width(2)
		# ctx.stroke()

		# # Show iterating and modifying a (text) path.
		# ctx.new_path()
		# ctx.move_to(0, 0)
		# ctx.set_source_rgb(0.3, 0.3, 0.3)
		# ctx.set_font_size(30)
		# text = "This path was warped..."
		# ctx.text_path(text)
		# tw, th = ctx.text_extents(text)[2:4]
		# self.warpPath(ctx, tw, th, 360,300)
		# ctx.fill()

		# Drawing a bitmap.  Note that we can easily load a PNG file
		# into a surface, but I wanted to show how to convert from a
		# wx.Bitmap here instead.  This is how to do it using just cairo :
		#img = cairo.ImageSurface.create_from_png(opj('bitmaps/toucan.png'))


		# img1 = wxcairo.ImageSurfaceFromBitmap(bmp)
		# ctx.set_source_surface(img1, 150, 150)
		# ctx.paint()

		# And this is how to convert a wx.Btmap to a cairo image
		# surface.  NOTE: currently on Mac there appears to be a
		# problem using conversions of some types of images.  They
		# show up totally transparent when used. The conversion itself
		# appears to be working okay, because converting back to
		# wx.Bitmap or writing the image surface to a file produces
		# the expected result.  The other platforms are okay.
		# bmp = wx.Bitmap(opj("C:\\Users\\marco\\Desktop\\testsvg\\pinup.png"))
		# img = wxcairo.ImageSurfaceFromBitmap(bmp)

		# ctx.set_source_surface(img, 70, 230)
		# ctx.paint()

		# # This is how to convert an image surface to a wx.Bitmap.
		# bmp2 = wxcairo.BitmapFromImageSurface(img)
		# dc.DrawBitmap(GetBmpFromSvg("KH", -3), 170, 150)
		# dc.DrawBitmap(GetBmpFromSvg("KD", 3), 200, 150)


	def warpPath(self, ctx, tw, th, dx, dy):
		"""
		...
		"""

		def f(x, y):
			xn = x - tw/2
			yn = y+ xn ** 3 / ((tw/2)**3) * 70
			return xn+dx, yn+dy

		path = ctx.copy_path()

		ctx.new_path()
		for type, points in path:
			if type == cairo.PATH_MOVE_TO:
				x, y = f(*points)
				ctx.move_to(x, y)

			elif type == cairo.PATH_LINE_TO:
				x, y = f(*points)
				ctx.line_to(x, y)

			elif type == cairo.PATH_CURVE_TO:
				x1, y1, x2, y2, x3, y3 = points
				x1, y1 = f(x1, y1)
				x2, y2 = f(x2, y2)
				x3, y3 = f(x3, y3)
				ctx.curve_to(x1, y1, x2, y2, x3, y3)

			elif type == cairo.PATH_CLOSE_PATH:
				ctx.close_path()

#---------------------------------------------------------------------------

class MyFrame(wx.Frame):
	"""
	...
	"""
	def __init__(self):
		super(MyFrame, self).__init__(None,
									  -1,
									  title="Sample_one")

		#------------

		# Simplified init method.
		self.SetProperties()
		self.CreateCtrls()
		self.BindEvents()
		self.DoLayout()

		#------------

		self.CenterOnScreen()

	#-----------------------------------------------------------------------

	def SetProperties(self):
		"""
		...
		"""

		self.SetMinSize((640, 400))
		self.SetSize((1280, 800))

		#------------

		# frameicon = wx.Icon("wxwin.ico")
		# self.SetIcon(frameicon)


	def CreateCtrls(self):
		"""
		...
		"""

		# Create a panel.
		self.panel = MyPanel(self)


	def BindEvents(self):
		"""
		Bind some events to an events handler.
		"""

		# Bind the close event to an event handler.
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)


	def DoLayout(self):
		"""
		...
		"""

		# MainSizer is the top-level one that manages everything.
		mainSizer = wx.BoxSizer(wx.VERTICAL)

		# Finally, tell the panel to use the sizer for layout.
		self.panel.SetAutoLayout(True)
		self.panel.SetSizer(mainSizer)

		mainSizer.Fit(self.panel)

	#-----------------------------------------------------------------------

	def OnCloseMe(self, event):
		"""
		...
		"""

		self.Close(True)


	def OnCloseWindow(self, event):
		"""
		...
		"""

		self.Destroy()

#---------------------------------------------------------------------------

class MyApp(wx.App):
	"""
	...
	"""
	def OnInit(self):

		#------------

		frame = MyFrame()
		self.SetTopWindow(frame)
		frame.CenterOnScreen(wx.BOTH)
		frame.Show(True)

		return True

#---------------------------------------------------------------------------

def main():
	app = MyApp(redirect=False)
	wx.lib.inspection.InspectionTool().Show()
	app.MainLoop()

#---------------------------------------------------------------------------


if __name__ == "__main__" :
	wx.Log.SetLogLevel(0)
	main()