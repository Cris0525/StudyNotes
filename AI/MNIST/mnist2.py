#-*-coding:utf-8-*-
from PIL import Image, ImageFilter
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import cv2
 
def sum_9_region_new(img, x, y):
	'''确定噪点 '''
	cur_pixel = img.getpixel((x, y))  # 当前像素点的值
	width = img.width
	height = img.height
 
	if cur_pixel == 1:  # 如果当前点为白色区域,则不统计邻域值
		return 0
 
	# 因当前图片的四周都有黑点，所以周围的黑点可以去除
	if y < 3:  # 本例中，前两行的黑点都可以去除
		return 1
	elif y > height - 3:  # 最下面两行
		return 1
	else:  # y不在边界
		if x < 3:  # 前两列
			return 1
		elif x == width - 1:  # 右边非顶点
			return 1
		else:  # 具备9领域条件的
			sum = img.getpixel((x - 1, y - 1)) \
				  + img.getpixel((x - 1, y)) \
				  + img.getpixel((x - 1, y + 1)) \
				  + img.getpixel((x, y - 1)) \
				  + cur_pixel \
				  + img.getpixel((x, y + 1)) \
				  + img.getpixel((x + 1, y - 1)) \
				  + img.getpixel((x + 1, y)) \
				  + img.getpixel((x + 1, y + 1))
			return 9 - sum
 
def collect_noise_point(img):
	'''收集所有的噪点'''
	noise_point_list = []
	for x in range(img.width):
		for y in range(img.height):
			res_9 = sum_9_region_new(img, x, y)
			if (0 < res_9 < 3) and img.getpixel((x, y)) == 0:  # 找到孤立点
				pos = (x, y)
				noise_point_list.append(pos)
	return noise_point_list
 
def remove_noise_pixel(img, noise_point_list):
	'''根据噪点的位置信息，消除二值图片的黑点噪声'''
	for item in noise_point_list:
		img.putpixel((item[0], item[1]), 1)
 
def get_bin_table(threshold=115):
	'''获取灰度转二值的映射table,0表示黑色,1表示白色'''
	table = []
	for i in range(256):
		if i < threshold:
			table.append(0)
		else:
			table.append(1)
	return table
 
def main1():
	image = Image.open('/home/cris/Study/AI/MNIST/image/text.png')
	imgry = image.convert('L')
	table = get_bin_table()
	binary = imgry.point(table, '1')
	noise_point_list = collect_noise_point(binary)
	remove_noise_pixel(binary, noise_point_list)
	binary.save('/home/cris/Study/AI/MNIST/image/finaly.png')

main1()

 
def imageprepare():
    file_name='/home/cris/Study/AI/MNIST/image/finaly.png'#导入自己的图片地址
    #进行灰度处理
    im = Image.open(file_name).convert('L')
    #将图片进行剪裁成28*28像素大小
    img = im.resize((28, 28), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
    img.show()
    data = list(img.getdata())
    #data = np.matrix(data,dtype="float")
    #data = (255.0 - data) / 255.0
    #重塑一个数组
    new_data = np.reshape(data, (1, 28 * 28))

    #normalize pixels to 0 and 1. 0 is pure white, 1 is pure black.
    tva = [ (255-x)*1.0/255.0 for x in data] 
    #print(tva)
    return tva

result=imageprepare()
x = tf.placeholder("float", shape=[None, 784])  
#训练标签数据  
y_ = tf.placeholder("float", shape=[None, 10])  
#把x更改为4维张量，第1维代表样本数量，第2维和第3维代表图像长宽， 第4维代表图像通道数, 1表示黑白  
x_image = tf.reshape(x, [-1,28,28,1])  
  
  
#第一层：卷积层  
conv1_weights = tf.get_variable("conv1_weights", [5, 5, 1, 32], initializer=tf.truncated_normal_initializer(stddev=0.1)) #过滤器大小为5*5, 当前层深度为1， 过滤器的深度为32  
conv1_biases = tf.get_variable("conv1_biases", [32], initializer=tf.constant_initializer(0.0))  
conv1 = tf.nn.conv2d(x_image, conv1_weights, strides=[1, 1, 1, 1], padding='SAME') #运用卷积函数,设置移动步长为1, 使用全0填充  
relu1 = tf.nn.relu( tf.nn.bias_add(conv1, conv1_biases) ) #激活函数Relu去线性化  
  
#第二层：最大池化层  
#池化层过滤器的大小为2*2, 移动步长为2，使用全0填充  
pool1 = tf.nn.max_pool(relu1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  
  
#第三层：卷积层  
conv2_weights = tf.get_variable("conv2_weights", [5, 5, 32, 64], initializer=tf.truncated_normal_initializer(stddev=0.1)) #过滤器大小为5*5, 当前层深度为32， 过滤器的深度为64  
conv2_biases = tf.get_variable("conv2_biases", [64], initializer=tf.constant_initializer(0.0))  
conv2 = tf.nn.conv2d(pool1, conv2_weights, strides=[1, 1, 1, 1], padding='SAME') #移动步长为1, 使用全0填充  
relu2 = tf.nn.relu( tf.nn.bias_add(conv2, conv2_biases) )  

#第四层：最大池化层  
#池化层过滤器的大小为2*2, 移动步长为2，使用全0填充  
pool2 = tf.nn.max_pool(relu2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  
  
#第五层：全连接层  
fc1_weights = tf.get_variable("fc1_weights", [7 * 7 * 64, 1024], initializer=tf.truncated_normal_initializer(stddev=0.1)) #7*7*64=3136把前一层的输出变成特征向量  
fc1_baises = tf.get_variable("fc1_baises", [1024], initializer=tf.constant_initializer(0.1))  
pool2_vector = tf.reshape(pool2, [-1, 7 * 7 * 64])  
fc1 = tf.nn.relu(tf.matmul(pool2_vector, fc1_weights) + fc1_baises)  
  
#为了减少过拟合，加入Dropout层  
keep_prob = tf.placeholder(tf.float32)  
fc1_dropout = tf.nn.dropout(fc1, keep_prob)  
  
#第六层：全连接层  
fc2_weights = tf.get_variable("fc2_weights", [1024, 10], initializer=tf.truncated_normal_initializer(stddev=0.1)) #神经元节点数1024, 分类节点10  
fc2_biases = tf.get_variable("fc2_biases", [10], initializer=tf.constant_initializer(0.1))  
fc2 = tf.matmul(fc1_dropout, fc2_weights) + fc2_biases  
  
#第七层：输出层  
# softmax  
y_conv = tf.nn.softmax(fc2)  
  
#定义交叉熵损失函数  
cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))  
  
#选择优化器，并让优化器最小化损失函数/收敛, 反向传播  
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)  
  
# tf.argmax()返回的是某一维度上其数据最大所在的索引值，在这里即代表预测值和真实值  
# 判断预测值y和真实值y_中最大数的索引是否一致，y的值为1-10概率  
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))  
  
# 用平均值来统计测试准确率  
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))  
  
 
#导入训练好的模型
sess = tf.InteractiveSession()
saver = tf.train.Saver()
tf.global_variables_initializer().run()
saver.restore(sess, "/home/cris/Study/AI/MNIST/save/model.ckpt")
#print("W1:", sess.run(conv1_weights)) # 打印v1、v2的值一会读取之后对比
#print("W2:", sess.run(conv1_biases))
prediction=tf.argmax(y_conv,1)
predint=prediction.eval(feed_dict={x: [result],keep_prob: 1.0}, session=sess)

print('recognize result:')
print(predint[0])

