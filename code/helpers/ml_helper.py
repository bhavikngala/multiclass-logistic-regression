from tensorflow.examples.tutorials.mnist import input_data
from scipy.cluster.vq import kmeans2
import numpy as np

def readMNISTData():
	mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
	return [mnist.train.images, mnist.train.labels,
			mnist.validation.images, mnist.validation.labels,
			mnist.test.images, mnist.test.labels]

# compute cluster centers and labels using kmeans
def applyKmeans2(data, numClusters):
	centroids, labels = kmeans2(data, numClusters, 
		iter=20, minit='points', missing='warn')
	return [centroids, labels]

# compute inverse of spreads for each clusters in the data
def computeClusterSpreadsInvs(data, lbls):
	lbls = np.array(lbls)
	data = np.array(data)

	unique_lbls = np.unique(lbls)
	
	numlbls = unique_lbls.shape[0]
	spreadInvCols = data.shape[1]
	spreadInvs = np.empty([numlbls, spreadInvCols, spreadInvCols])

	for lbl in unique_lbls:
		lbl_indices = np.nonzero(lbls == lbl)
		lbl_cluster = data[lbl_indices]

		var = np.var(lbl_cluster, axis=0)
		spread = var * np.identity(lbl_cluster.shape[1])
		spreadInv = np.linalg.pinv(spread)

		spreadInvs[lbl, :, :] = spreadInv

	return spreadInvs

# compute design matrix of data
def computeDesignMatrixUsingGaussianBasisFunction(data, means, 
	spreadInvs):
	numDataRows = data.shape[0]
	numBasis = means.shape[0]

	designMatrix = np.empty([numDataRows, numBasis])

	rowIndex = 0
	for (mean, spreadInv) in zip(means, spreadInvs):
		distFromMean = data - mean
		firstBasis = np.sum(np.multiply(
			np.matmul(distFromMean, spreadInv)), axis=1)
		firstBasis = np.exp(-0.5 * firstBasis)
		designMatrix[:, rowIndex] = firstBasis
		rowIndex = rowIndex + 1

	return np.insert(designMatrix, 0, 1, axis=1)

# function provided by TA
def computeWeightsUsingSGD(designMatrix, ouputData, learningRate,
	epochs, batchSize, l2Lambda):
	N,M = designMatrix.shape
	weights = np.zeros([1, M])

	for epoch in range(epochs):
		for i in range(int(N/batchSize)):
			lowerBound = i * batchSize
			upperBound = min((i+1)*batchSize, N)

			phi = designMatrix[lowerBound:upperBound, :]

			target = ouputData[lowerBound:upperBound, :]

			ED = np.matmul(sigmoid((np.matmul(phi, weights.T))\
				 - target).T, phi)
			E = (ED + l2Lambda * weights)/batchSize

			weights = weights - learningRate * E

	return weights

def computeWeightsSetUsingSGD(designMatrix, ouputData, learningRate,
	epochs, batchSize, l2Lambda):
	N,M = designMatrix.shape
	K = ouputData.shape[1]

	weights = np.zeros([K, M])

	for epoch in range(epochs):
		for i in range(int(N/batchSize)):
			# determine the inputs/outputs in batch
			lowerBound = i * batchSize
			upperBound = min((i + 1) * batchSize, N)

			phi = designMatrix[lowerBound:upperBound, :]
			target = ouputData[lowerBound:upperBound, :]

			# predict class for batch
			predictedClasses = predictClass(phi, weights)

			# compute error gradient for each class
			errorGradients = computeErrorGradient(phi, 
				predictedClasses, target)

			# add regularizer
			error = (errorGradients + l2Lambda * weights)/batchSize

			# update weights
			weights = weights - learningRate * errror

	return weights

def predictClass(data, weights):
	predictedClasses = np.zeros([data,shape[0], weights.shape[0]])
	data = np.insert(data, 0, 1, axis=1)

	rowIndex = 0
	for singleData in data:
		classProbNum = np.sum(np.multiply(singleData, weights),
			axis=1)
		classProbs = classProbNum/np.sum(classProbNum)
		predictedClasses[rowIndex, :] = classProbs
		rowIndex = rowIndex + 1

	return predictedClasses

def computeErrorGradient(data, predictedClasses, target):
	errorGradients = np.zeros([predictedClasses.shape[1],
		data.shape[0]])

	diff = predictedClasses - target
	
	for i in range(predictedClasses.shape[1]):
		errorGradients[i, :] = \
			np.sum(np.multiply(diff[:, i], data), axis=0)

	return errorGradients