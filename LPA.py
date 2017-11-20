from PIL import Image
from random import randrange


class ImageProcessing:
	def __init__(self, filename):
		self.img = Image.open(filename)
		self.bytes = self.img.tobytes()
		self.bytesFresh = True
		self.iwidth, self.iheight = self.img.size
		self.pixels = []
		self.getRGB()

	def getRGB(self):
		bitarr = self.bytes
		pixelSize = len(bitarr) // self.iheight // self.iwidth
		for y in range(self.iheight):
			xcur = []
			for x in range(self.iwidth):
				temp = []
				for z in range(3):
					temp.append(int(bitarr[(self.iwidth * y + x) * pixelSize + z]))
				xcur.append(temp)
			self.pixels.append(xcur)

	def kmeans(self, k, seedGen=None, show=False, toFile=False, verbose=False):
		if seedGen is None:
			cluster = self.randomSeeds(k)
		else:
			cluster = seedGen(k)
		assignments = [[-1 for x in range(self.iwidth)] for y in range(self.iheight)]
		iterCount = 0

		while True:
			iterCount += 1
			reassignment = 0
			sse = [0 for x in range(k)]
			newCluster = [[0, 0, 0, 0] for x in range(k)]
			for x in range(self.iheight):
				for y in range(self.iwidth):
					minSim = 1000
					index = -1
					for z in range(k):
						minSim, index = min((minSim, index), (self.imageSimilarity(cluster[z], self.pixels[x][y]), z))
					if assignments[x][y] != index:
						assignments[x][y] = index
						reassignment += 1
					sse[index] += minSim
					newCluster[index] = [
						newCluster[index][z] + self.pixels[x][y][z] if z < 3 else newCluster[index][z] + 1
						for z in range(4)]
			newCluster = [
				[newCluster[x][y] // newCluster[x][3] if newCluster[x][3] != 0 else newCluster[x][y] for y
				 in range(3)] for x in range(k)]

			if verbose:
				print('iteration number:', iterCount)
				print('old cluster:', cluster, sep='\n')
				print('new cluster:', newCluster, sep='\n')
				print('number of reassignments:', reassignment)
				print('cluster SSE', sse, '\n')

			if toFile or show:
				fn = self.getFilename('kmean', k, iterCount)
				tempData = [[newCluster[assignments[x][y]] for y in range(self.iwidth)] for x in range(self.iheight)]
				self.toImage(tempData, show=show, toFile=toFile, filename=fn)

			if self.kmterminate(k, cluster, newCluster):
				return
			cluster = newCluster

	def kmterminate(self, k, old, new):
		for x in range(k):
			change = 0
			for y in range(3):
				temp = abs(old[x][y] - new[x][y])
				if temp > 1:
					return False
				change += temp
			if change > 3:
				return False
		return True

	def imageSimilarity(self, a, b):
		rmean = (a[0] + b[0]) // 2
		rdiff = a[0] - b[0]
		gdiff = a[1] - b[1]
		bdiff = a[2] - b[2]
		return ((((512 + rmean) * rdiff * rdiff) >> 8) + 4 * gdiff * gdiff + (
			((767 - rmean) * bdiff * bdiff) >> 8)) ** 0.5

	def randomSeeds(self, k):
		output = set()
		while len(output) != k:
			output.add((randrange(0, self.iheight), randrange(0, self.iwidth)))
		output = [self.pixels[x[0]][x[1]] for x in output]
		return list(output)

	def getFilename(self, method, k, iteration):
		return 'output/' + method + '_' + str(k) + '_' + str(iteration) + '.png'

	def toImage(self, data=None, show=True, toFile=False, filename=''):
		tempImg = Image.frombuffer('RGB', (self.iwidth, self.iheight), bytes(self.toByteArr(data)), 'raw', 'RGB', 0, 1)
		if show:
			tempImg.show()
		if toFile:
			tempImg.save(filename, 'png')

	def toByteArr(self, data=None):
		if data is None:
			if not self.bytesFresh:
				self.bytes = [z for x in self.pixels for y in x for z in y]
				self.bytes = bytearray(self.bytes)
				self.bytesFresh = True
			return self.bytes
		else:
			output = [z for x in data for y in x for z in y]
			output = bytearray(output)
			return output


if __name__ == '__main__':
	tester = ImageProcessing('imageData/image003.jpg')
	# tester.toImage()
	tester.kmeans(int(input("Enter k:")), toFile=True, verbose=True)


# TODO do i even need to make 3d array and change to int?
# TODO can kmean be optimized? 
# TODO cluster only if touching
# TODO B
