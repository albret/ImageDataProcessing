from PIL import Image
from random import randrange
from time import time


class ImageProcessing:
	def __init__(self, filename):
		self.img = Image.open(filename)
		temp = self.img.tobytes()
		self.iwidth, self.iheight = self.img.size
		pixelSize = len(temp) // self.iheight // self.iwidth
		self.pixels = [temp[x] for x in range(len(temp)) if x % pixelSize < 3]
		self.bytesFresh = True

	def kmeans(self, k, seedGen=None, show=False, toFile=False, verbose=False):
		if seedGen is None:
			cluster = self.randomSeeds(k)
		else:
			cluster = seedGen(k)
		assignments = [[-1 for x in range(self.iwidth)] for y in range(self.iheight)]
		iterCount = 0

		while True:
			start = time()
			iterCount += 1
			reassignment = 0
			sse = [0 for x in range(k)]
			newCluster = [[0, 0, 0] for x in range(k)]
			clusterSize = [0 for x in range(k)]
			for x in range(self.iheight):
				for y in range(self.iwidth):
					pos = (x * self.iwidth + y) * 3
					cur = self.pixels[pos:pos + 3]
					minSim = 1000
					index = -1
					for z in range(k):
						minSim, index = min((minSim, index), (self.imageSimilarity(cluster[z], cur), z))
					if assignments[x][y] != index:
						assignments[x][y] = index
						reassignment += 1
					sse[index] += minSim
					newCluster[index] = [newCluster[index][z] + cur[z] for z in range(3)]
					clusterSize[index] += 1
				print(x)
			if 0 in clusterSize:
				if verbose:
					print('empty cluster detected')
				clusterSize = [x if x != 0 else 1 for x in clusterSize]
			newCluster = [[newCluster[x][y] // clusterSize[x] for y in range(3)] for x in range(k)]

			if verbose:
				print('k = ', k, '\titer = ', iterCount, '\ttime:', time() - start)
				print('old cluster:', cluster, sep='\n')
				print('new cluster:', newCluster, sep='\n')
				print('number of reassignments:', reassignment)
				print('cluster SSE', sse, '\n')

			if toFile or show:
				fn = self.getFilename('kmean', k, iterCount)
				tempData = [z for x in assignments for y in x for z in newCluster[y]]
				self.toImage(tempData, show=show, toFile=toFile, filename=fn)

			if self.kmterminate(k, cluster, newCluster):
				return
			cluster = newCluster

	def kmterminate(self, k, old, new):
		for x in range(k):
			change = 0
			for y in range(3):
				temp = abs(old[x][y] - new[x][y])
				if temp > 2:
					return False
				change += temp
			if change > 6:
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
		output = [self.pixels[(x[0] * self.iwidth + x[1]) * 3:((x[0] * self.iwidth + x[1]) * 3) + 3] for x in output]
		return list(output)

	def getFilename(self, method, k, iteration):
		return 'output/' + method + '_' + str(k) + '_' + str(iteration) + '.png'

	def toImage(self, data=None, show=True, toFile=False, filename=''):
		tempData = bytes(bytearray(self.pixels if data is None else data))
		tempImg = Image.frombuffer('RGB', (self.iwidth, self.iheight), tempData, 'raw', 'RGB', 0, 1)
		if show:
			tempImg.show()
		if toFile:
			tempImg.save(filename, 'png')


if __name__ == '__main__':
	tester = ImageProcessing('imageData/image003.jpg')
	# tester.toImage()
	# tester.kmeans(int(input("Enter k:")), toFile=True, verbose=True)
	tester.kmeans(2, toFile=True, verbose=True)


# TODO can kmean be optimized? 
# TODO cluster only if touching
# TODO B
