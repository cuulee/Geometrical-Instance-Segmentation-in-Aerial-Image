import numpy as np
import tensorflow as tf
from Config import *
config = Config()

def VGG16(img, reuse = None):
	"""
		img: [batch_size, height, width, num_channels]
	"""
	with tf.variable_scope('VGG16', reuse = reuse):
		conv1_1 = tf.layers.conv2d       (inputs = img    , filters =  64, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) # 256
		conv1_2 = tf.layers.conv2d       (inputs = conv1_1, filters =  64, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) # 256
		pool1   = tf.layers.max_pooling2d(inputs = conv1_2, pool_size = (2, 2), strides = 2)												# 128
		conv2_1 = tf.layers.conv2d       (inputs = pool1  , filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) # 128
		conv2_2 = tf.layers.conv2d       (inputs = conv2_1, filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) # 128
		pool2   = tf.layers.max_pooling2d(inputs = conv2_2, pool_size = (2, 2), strides = 2)												#  64
		conv3_1 = tf.layers.conv2d       (inputs = pool2  , filters = 256, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  64
		conv3_2 = tf.layers.conv2d       (inputs = conv3_1, filters = 256, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  64
		conv3_3 = tf.layers.conv2d       (inputs = conv3_2, filters = 256, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  64
		pool3   = tf.layers.max_pooling2d(inputs = conv3_3, pool_size = (2, 2), strides = 2)												#  32
		conv4_1 = tf.layers.conv2d       (inputs = pool3  , filters = 512, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		conv4_2 = tf.layers.conv2d       (inputs = conv4_1, filters = 512, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		conv4_3 = tf.layers.conv2d       (inputs = conv4_2, filters = 512, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		pool4   = tf.layers.max_pooling2d(inputs = conv4_3, pool_size = (2, 2), strides = 2)												#  16
		conv5_1 = tf.layers.conv2d       (inputs = pool4  , filters = 512, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  16
		conv5_2 = tf.layers.conv2d       (inputs = conv5_1, filters = 512, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  16
		conv5_3 = tf.layers.conv2d       (inputs = conv5_2, filters = 512, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  16
		return pool2, pool3, conv3_3, conv4_3, conv5_3

def PolygonRNNFeature(vgg_result, crop_info, reuse = None):
	"""
		vgg_result: see the return of VGG16 function defined above
	"""
	pool2, pool3, _, conv4_3, conv5_3 = vgg_result
	idx = tf.cast(crop_info[:, 0], tf.int32)
	pool2   = tf.image.crop_and_resize(pool2  , crop_info[:, 1: 5], idx, config.PATCH_SIZE_4 )
	pool3   = tf.image.crop_and_resize(pool3  , crop_info[:, 1: 5], idx, config.PATCH_SIZE_8 )
	conv4_3 = tf.image.crop_and_resize(conv4_3, crop_info[:, 1: 5], idx, config.PATCH_SIZE_8 )
	conv5_3 = tf.image.crop_and_resize(conv5_3, crop_info[:, 1: 5], idx, config.PATCH_SIZE_16)
	with tf.variable_scope('PolygonRNNFeature', reuse = reuse):
		inter1  = tf.layers.max_pooling2d(inputs = pool2  , pool_size = (2, 2), strides = 2)												#  32
		part1   = tf.layers.conv2d       (inputs = inter1 , filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		part2   = tf.layers.conv2d       (inputs = pool3  , filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		part3   = tf.layers.conv2d       (inputs = conv4_3, filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		inter4  = tf.layers.conv2d       (inputs = conv5_3, filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  16
		part4   = tf.image.resize_images (images = inter4 , size = [inter4.shape[1] * 2, inter4.shape[2] * 2])								#  32
		inter_f = tf.concat([part1, part2, part3, part4], axis = 3)																			#  32
		feature = tf.layers.conv2d       (inputs = inter_f, filters = 128, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		return feature

def PyramidAnchorFeature(vgg_result, reuse = None):
	"""
		vgg_result: see the return of VGG16 function defined above
	"""
	_, _, conv3_3, conv4_3, conv5_3 = vgg_result
	with tf.variable_scope('PyramidAnchorFeature', reuse = reuse):
		c5      = tf.layers.conv2d       (inputs = conv5_3, filters = 256, kernel_size = (1, 1), padding = 'same', activation = tf.nn.relu) #  16
		c4      = tf.layers.conv2d       (inputs = conv4_3, filters = 256, kernel_size = (1, 1), padding = 'same', activation = tf.nn.relu) #  32
		c4     += tf.image.resize_images (images = c5, size = [c5.shape[1] * 2, c5.shape[2] * 2])											#  32
		c3      = tf.layers.conv2d       (inputs = conv3_3, filters = 256, kernel_size = (1, 1), padding = 'same', activation = tf.nn.relu) #  64
		c3     += tf.image.resize_images (images = c4, size = [c4.shape[1] * 2, c4.shape[2] * 2])											#  64
		p3      = tf.layers.conv2d       (inputs = c3     , filters = 256, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  64
		p4      = tf.layers.conv2d       (inputs = c4     , filters = 256, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  32
		p5      = tf.layers.conv2d       (inputs = c5     , filters = 256, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #  16
		p6      = tf.layers.max_pooling2d(inputs = p5     , pool_size = (2, 2), strides = 2)												#   8
	return p3, p4, p5, p6

def SingleLayerFPN(feature, anchors_per_pixel, reuse = None):
	"""
		feature: [batch_size, height, width, num_channels]
		anchors_per_pixel: scalar
	"""
	a = anchors_per_pixel
	num_anchors = feature.shape[1] * feature.shape[2] * a
	with tf.variable_scope('SingleLayerFPN', reuse = reuse):
		inter   = tf.layers.conv2d       (inputs = feature, filters = 512, kernel_size = (3, 3), padding = 'same', activation = tf.nn.relu) #   ?
		logit   = tf.layers.conv2d       (inputs = inter  , filters = 2*a, kernel_size = (1, 1), padding = 'valid', activation = None)		#   ?
		delta   = tf.layers.conv2d       (inputs = inter  , filters = 4*a, kernel_size = (1, 1), padding = 'valid', activation = None)		#   ?
	return tf.reshape(logit, [-1, num_anchors, 2]), tf.reshape(delta,  [-1, num_anchors, 4])

