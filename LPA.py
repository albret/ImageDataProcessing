from PIL import Image
from random import randrange


class ImageProcessing:
	def __init__(self, filename):
		self.img = Image.open(filename)
		self.bytes = self.img.tobytes()
		self.bytesFresh = False
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

	def imageSimilarity(self, a, b):
		rmean = (a[0] + b[0]) // 2
		rdiff = a[0] - b[0]
		gdiff = a[1] - b[1]
		bdiff = a[2] - b[2]
		return ((((512 + rmean) * rdiff * rdiff) >> 8) + 4 * gdiff * gdiff + (
			((767 - rmean) * bdiff * bdiff) >> 8)) ** 0.5

	def toImage(self, data=None):
		tempImg = Image.frombuffer('RGB', (self.iwidth, self.iheight), bytes(self.toByteArr(data)), 'raw', 'RGB', 0, 1)
		tempImg.show()

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

	def kmeans(self, k, seedGen=None):
		if seedGen is None:
			cluster = self.randomSeeds(k)
		else:
			cluster = seedGen(k)
		assignments = [[-1 for x in range(self.iwidth)] for y in range(self.iheight)]
		reassignment = self.iwidth * self.iheight
		iterCount = 1

		while reassignment > int(self.iwidth * self.iheight * 0.02):
			reassignment = 0
			sse = [0 for x in range(k)]
			clusterUpdate = [[0, 0, 0, 0] for x in range(k)]
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
					clusterUpdate[index] = [
						clusterUpdate[index][z] + self.pixels[x][y][z] if z < 3 else clusterUpdate[index][z] + 1
						for z in range(4)]
			print('iteration number:', iterCount)
			print('old cluster:', cluster, sep='\n')
			cluster = [[clusterUpdate[x][y] // clusterUpdate[x][3] for y in range(3)] for x in range(k)]
			print('new cluster:', cluster, sep='\n')
			print('number of reassignments:', reassignment)
			print('cluster SSE', sse)
			iterCount += 1
			self.toImage([[cluster[assignments[x][y]] for y in range(self.iwidth)] for x in range(self.iheight)])

	def randomSeeds(self, k):
		output = set()
		while len(output) != k:
			output.add((randrange(0, self.iheight), randrange(0, self.iwidth)))
		output = [self.pixels[x[0]][x[1]] for x in output]
		return list(output)


if __name__ == '__main__':
	tester = ImageProcessing('image000.jpg')
	tester.toImage()
	tester.kmeans(int(input("Enter k:")))

# TODO k means
# TODO visualize
# TODO B
