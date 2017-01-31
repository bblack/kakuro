#!/usr/bin/python
# Python solver
# Last modified 2009/02/22

import cairo
import os
import copy
import sys
import time

class KakuroBoard:

	width = 0
	height = 0

	squares = []

	def __init__(self):
		return
	
	def isSolved(self):
		for i in self.squares:
			if i.black == 0 and len(i.possibleValues) > 1:
				return False
		return True
	
	def eliminateValues(self, rownum, colnum):
		sq = self.getSquare(rownum, colnum)
		if sq.black == 1:
			return
		sq.possibleValues = self.getPossibleValues(rownum, colnum)		
		self.setSquare(rownum, colnum, sq)
		
		return
		
	def setSquare(self, rownum, colnum, sq):
		self.squares[rownum*self.width + colnum] = sq
		return
	
	def firstIteration(self):
		# This should be run FIRST, and only once.
		for rownum in range(self.height):
			for colnum in range(self.width):
				self.eliminateValues(rownum, colnum)
		return
	
	def secondIteration(self):
		# This runs until the board is solved.
		
		for square in self.squares:
			
			# THIS IS FOR COLUMNS
			if square.downTotal > 0:
				square.lastincol = self.getSquare(square.location[0] + 1, square.location[1]).lastincol
				col = []
				for x in range(square.location[0] + 1, square.lastincol[0] + 1):
					col.append(self.getSquare(x, square.location[1]))
				# Now col is the set of squares in the column
				
				#print "Col is: " + str(col)
				colsums = getSums2(square.downTotal, col)
				
				newpossiblevalues = []
				for i in range(len(col)):
					newpossibles = []
					for j in colsums:
						if j[i] not in newpossibles: newpossibles.append( j[i] )
					col[i].possibleValues = newpossibles
					self.setSquare(col[i].location[0], col[i].location[1], col[i])
					
			# THIS IS FOR ROWS
			if square.rightTotal > 0:
				square.lastinrow = self.getSquare(square.location[0], square.location[1] + 1).lastinrow
				row = []
				for x in range(square.location[1] + 1, square.lastinrow[1] + 1):
					row.append(self.getSquare(square.location[0], x))
				# Now row is the set of squares in the row
				
				rowsums = getSums2(square.rightTotal, row)
				
				newpossiblevalues = []
				for i in range(len(row)):
					newpossibles = []
					for j in rowsums:
						if j[i] not in newpossibles: newpossibles.append( j[i] )
					row[i].possibleValues = newpossibles
					self.setSquare(row[i].location[0], row[i].location[1], row[i])				
		return
	
	def getPossibleValues(self, rownum, colnum):
		# Returns a list of possible values for the square at rownum, colnum
		# based on the intersection of possible values for sums in the row and column
		
		possibleinrow = []
		possibleincol = []
		
		# First, find the row total square
		rts = self.getSquare(rownum, colnum)
		while rts.rightTotal == 0:
			rts = self.getSquare( rownum, rts.location[1] - 1 )
			
		# Then find the last square of the row
		lastinrow = self.getSquare(rownum, colnum)
		while 1:
			if self.getSquare(rownum, lastinrow.location[1] + 1) == None:
				break
			if self.getSquare(rownum, lastinrow.location[1] + 1).black == 1:
				break
			lastinrow = self.getSquare(rownum, lastinrow.location[1] + 1)
			
		# Save this
		self.getSquare(rownum, colnum).lastinrow = lastinrow.location
		
		# This is the row length
		rowlen = lastinrow.location[1] - rts.location[1]
		
		# Get all digits in all possible row sums
		for i in getSums(rts.rightTotal, rowlen):
			for digit in i:
				if digit not in possibleinrow:
					possibleinrow.append(digit)
					

		# Now, find the col total square
		cts = self.getSquare(rownum, colnum)
		while cts.downTotal == 0:
			cts = self.getSquare( cts.location[0] - 1, colnum )
			
		# Then find the last square of the column
		lastincol = self.getSquare(rownum, colnum)
		while 1:
			if self.getSquare(lastincol.location[0] + 1, colnum) == None:
				break
			if self.getSquare(lastincol.location[0] + 1, colnum).black == 1:
				break
			lastincol = self.getSquare(lastincol.location[0] + 1, colnum)
			
		# Save this
		self.getSquare(rownum, colnum).lastincol = lastincol.location
			
		# This is the col length
		collen = lastincol.location[0] - cts.location[0]
		
		# Get all digits in all possible col sums
		for i in getSums(cts.downTotal, collen):
			for digit in i:
				if digit not in possibleincol:
					possibleincol.append(digit)
					
		# Find intersection
		possiblevalues = []
		for i in possibleinrow:
			if i in possibleincol:
				possiblevalues.append(i)
				
		#print "Possible values for (%i,%i):" % (rownum, colnum)
		#print possiblevalues
						
		return possiblevalues
			
		
		
				
	def getSquare(self, rownum, colnum):
		if rownum*self.width + colnum >= len(self.squares):
			return None
		else:
			return self.squares[rownum*self.width + colnum]
	
	def buildFromFile(self, file):
		f = open(file)
		self.buildFromString(f.read().replace('\n','').replace(' ','').replace('\t',''))
		f.close()
		
	def buildFromString(self, instr):
		# comma delimited
		# w,h,square,square, ...
		# w is white
		# b is black
		# d34 is down 34
		# r21 is right 21
		# d34r21 is both
		tokens = instr.split(',')
		self.width = int(tokens[0])
		self.height = int(tokens[1])
		tokens = tokens[2:]
		squares = []
		for t in range(len(tokens)):
			i = tokens[t]
			s = KakuroSquare()
			
			s.location = (t/self.width, t%self.width)
			
			if i.startswith('w'):
				s.black = 0
			elif i.startswith('b'):
				s.black = 1
			elif i.startswith('d') and i.find('r') > -1:
				s.black = 1
				s.downTotal = int(i[1:i.find('r')])
				s.rightTotal = int(i[i.find('r')+1:])
			elif i.startswith('d'):
				s.black = 1
				s.downTotal = int(i[1:])
			elif i.startswith('r'):
				s.black = 1
				s.rightTotal = int(i[1:])
			else:
				print "invalid square read: " + i
			self.squares.append(s)
		return
		
	def drawToPng(self, file):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 48*self.width+2, 48*self.height+2)
		cr = cairo.Context(surface)
		
		for rownum in range(self.height):
			for colnum in range(self.width):
				x, y = 48*colnum, 48*rownum
				squarenum = rownum*self.width + colnum
				
				cr.set_source_rgb(0,0,0)
				cr.rectangle(x, y, 50, 50)
				cr.fill()

				cr.set_source_rgb(1,1,1)
				cr.rectangle(x+2, y+2, 46, 46)
				cr.fill()
				
				#print self.squares[squarenum]
				
				
				if self.squares[squarenum].black == 1:
					cr.set_source_rgb(0,0,0)
					cr.rectangle(x+4, y+4, 42, 42)
					cr.fill()
				else:
					cr.set_source_rgb(.5,0,0)
					cr.select_font_face("Swis721 Cn BT")
					cr.set_font_size(10)
					cr.move_to(x+3,y+25)
					s = ''
					for i in self.squares[squarenum].possibleValues:
						s += (str(i))
					cr.show_text(s)
					
					if len(s) == 1:
						cr.set_source_rgb(1,.2,.2)
						cr.set_font_size(40)
						cr.move_to(x+27, y+36)
						cr.show_text(s)
						
					cr.set_font_size(10)
					cr.set_source_rgb(0,.5,0)
					cr.move_to(x+3,y+12)
					cr.show_text(str(self.squares[squarenum].location))
					

					
				if self.squares[squarenum].downTotal > 0:
					cr.set_line_width(2)
					cr.set_source_rgb(1,1,1)
					cr.move_to(x+4,y+4)
					cr.line_to(x+46,y+46)
					cr.stroke()
					
					cr.select_font_face("Swis721 Cn BT", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
					cr.set_font_size(20)
					cr.move_to(x+5, y+44)
					cr.show_text( str(self.squares[squarenum].downTotal) )
					
				if self.squares[squarenum].rightTotal > 0:
					cr.set_line_width(2)
					cr.set_source_rgb(1,1,1)
					cr.move_to(x+4,y+4)
					cr.line_to(x+46,y+46)
					cr.stroke()
					
					cr.select_font_face("Swis721 Cn BT", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
					cr.set_font_size(20)
					cr.move_to(x+25, y+22)
					cr.show_text( str(self.squares[squarenum].rightTotal) )
				
				cr.set_font_size(9)
				
				cr.set_source_rgb(1,0,0)
				cr.move_to(x+3, y+45)
				#cr.show_text( str(self.squares[squarenum].lastinrow))
				
				cr.set_source_rgb(0,0,1)
				cr.move_to(x+3, y+34)
				#cr.show_text( str(self.squares[squarenum].lastincol))
	
		cr.scale(0.5,0.5)
		print "Writing " + file
		surface.write_to_png(file)


class KakuroSquare:
	
	black = 0 # 1 if square is black, 0 if square is white	
	downTotal = 0
	rightTotal = 0
	
	location = (-1,-1) # valid values start with 0: row,col
	rts = (-1, -1) # the location of the row-total-square to which this one belongs
	cts = (-1, -1) # the location of the column-total-square to which this one belongs
	lastinrow = (-1, -1) #the last white space in this row
	lastincol = (-1, -1) # the last white space in this column
	
	possibleValues = range(1,10) # digits 1-9
	
	
	
	def __init__(self):
		return

	def __str__(self):
		return "black=%i, down=%i, right=%i" % (self.black, self.downTotal, self.rightTotal)

	def __repr__(self):
		return "Square: " + str(self.possibleValues) + " at " + str(self.location)

	def copy(self):
		return copy.deepcopy(self)

def getSums(total, n, digits=range(1,10)):
	# Get all sums of length n that total total
	
	sums = []
	
	if n == 1 and total in digits:
		return [[total]]
	elif n == 1 and total not in digits:
		return []
	else:
		for i in digits:
			d = list(digits)
			d.remove(i)
			tailSums = getSums(total-i, n-1, d)
			if tailSums != []:
				for j in tailSums:
					if j.count(i) == 0:
						j.append(i)
						# unnecessary slowdown?
						j.sort()
						if sums.count(j) == 0:
							sums.append(j)
		return sums
	
def getSums2(total, squarelist):
	# Get all ORDERED sums possible given the squarelist
	
	#print "GETTING SUMS:"
	#print str (total)
	#for i in squarelist:
	#	print i.possibleValues
	
	orderedsums = []
	
	if len(squarelist) == 1 and total in squarelist[0].possibleValues:
		#print "Singleton sum. returning...."
		return [[total]]
	elif len(squarelist) == 1 and total not in squarelist[0].possibleValues:
		#print "Invalid singleton sum. returning..."
		return []
	else:
		for i in squarelist[0].possibleValues:
			templist = []
			for square in squarelist[1:]:
				templist.append(square.copy())
			for othersquare in templist:
				if i in othersquare.possibleValues: othersquare.possibleValues.remove(i)

			#print "[i]: " + str([i]	)
			#print "Total - i: " + str(total - i)
			#print "Templist: " + str(templist)
			smallerSums = getSums2(total - i, templist)
			#print "    "*len(squarelist) + "smallerSums: " + str(smallerSums)
			
			smallerSums = getSums2(total - i, templist)
			if smallerSums != []:
				for s in smallerSums:
					aSum = [i]
					aSum.extend(s)
					orderedsums.append( aSum )
		return orderedsums




board = KakuroBoard()
starttime = time.time()

try:
	board.buildFromFile(sys.argv[1])
except:
	print "Could not read from file"
	exit()
	
outdir = 'output_' + sys.argv[1]

try:
	os.mkdir(outdir)
except OSError:
	print "Directory exists, continuing..."

board.firstIteration()
board.drawToPng( os.path.join(outdir, '1.png') )
i = 2
while not board.isSolved():
	if i > 50: break
	board.secondIteration()
	board.drawToPng( os.path.join(outdir, '%i.png' % i) )
	#print i
	i += 1
	
print 'Executed in ' + str(time.time() - starttime) + ' seconds'
	
# THIS IS NOT DECIDING
# SINCE IT ONLY TERMINATES ON A SOLVED BOARD
