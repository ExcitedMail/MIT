#-*- coding: utf-8 -*-
from ctypes import util
from operator import truediv
import cv2 as cv
import cvzone
import sys
import time
import copy
import numpy as np
import utils
import glob
import os
from tqdm import trange
from random import randint

import BAKA


# Create 2D list to store parts

basic_files = []
special_files = []
# remove anything from the list that is not a file (directories, symlinks)
# thanks to J.F. Sebastion for pointing out that the requirement was a list 
# of files (presumably not including directories)  

# sort file by modify time
# normal parts
for subDir in utils.PARTS:
	subfiles = list(filter(os.path.isfile, glob.glob(utils.SEARCH_DIR + subDir + "*")))
	subfiles.sort(key=lambda x: os.path.getmtime(x))
	basic_files.append(subfiles)

#special parts
for subDir in utils.SPECIAL_PARTS:
	subfiles = list(filter(os.path.isfile, glob.glob(utils.SEARCH_DIR + subDir + "*")))
	subfiles.sort(key=lambda x: os.path.getmtime(x))
	special_files.append(subfiles)



def produce_image(current_image, current_part, prev_part):
	# remove element by list.pop(INDEX)
	# Change those require by current_part (undone)

	

	# set if body is special
	# if(current_part.mode89 == False and current_part.part[0] == '' and randint(0, 10) < 2):
	# 	body_special = True
	# 	current_part.special = True
	# else:
	# 	body_special = False


	# initialize background
	b, g, r = randint(0, 256), randint(0, 256), randint(0, 256)
	current_image[:] = (b, g, r)


	# get random file parts if body special
	if(current_part.special):
		current_index = [2, 3, 4]
		rand_num = randint(0, len(special_files[0])-1)
		part = cv.imread(special_files[0][rand_num], cv.IMREAD_UNCHANGED)
		current_part.part[0] = special_files[0][rand_num]
		current_image = cvzone.overlayPNG(current_image, part, [0, 0])
	elif(current_part.mode89):
		current_index = [0, 2, 4, 6, 8]
	else:
		current_index = [1, 3, 5, 7, 9]
	

	# set else parts
	for i in current_index:
		if(current_part.part[i] != ''):
			part = cv.imread(current_part.part[i], cv.IMREAD_UNCHANGED)
		else:
			rand_num = randint(0, len(basic_files[i])-1)
			while(basic_files[i][rand_num] == prev_part.part[i]):
				# print('rechoose')
				rand_num = randint(0, len(basic_files[i])-1)
			part = cv.imread(basic_files[i][rand_num], cv.IMREAD_UNCHANGED)
			current_part.part[i] = basic_files[i][rand_num]
		# print(i, current_part.part[i])
		current_image = cvzone.overlayPNG(current_image, part, [0, 0])

	return current_image, current_part

		


		# if(body_special):
		# 	# get special body
		# 	rand_num = randint(0, len(special_files[0])-1)
		# 	part = cv.imread(special_files[0][rand_num], cv.IMREAD_UNCHANGED)
		# 	result = cvzone.overlayPNG(result, part, [0, 0])
			
		# 	for subDir in files[1:4]:
		# 		rand_num = randint(0, len(subDir)-1)
		# 		part = cv.imread(subDir[rand_num], cv.IMREAD_UNCHANGED)
		# 		result = cvzone.overlayPNG(result, part, [0, 0])
		# else:
		# 	# get random file parts if not special
		# 	for subDir in files:
		# 		rand_num = randint(0, len(subDir)-1)
		# 		part = cv.imread(subDir[rand_num], cv.IMREAD_UNCHANGED)
		# 		result = cvzone.overlayPNG(result, part, [0, 0])


		
		# cv.imwrite(utils.OUTPUT_PATH + utils.PROJ_NAME + format(index_img, '03d') + utils.OUTPUT_IMGTYPE, result)

baka = []
for num_img in range(utils.NUM_DISTRIB):
	baka.append(BAKA.baka_struct())

print('baka init finish.')

for num_img in trange(utils.NUM_DISTRIB):
	baka[num_img].image1, baka[num_img].type1 = produce_image(baka[num_img].image1, baka[num_img].type1, baka[num_img].typePrev)
	cv.imwrite(utils.OUTPUT_PATH + str(num_img) + 'A' + utils.OUTPUT_IMGTYPE, baka[num_img].image1)
	# cv.imwrite(utils.OUTPUT_PATH + utils.PROJ_NAME + format(num_img, '03d') + '/A' + utils.OUTPUT_IMGTYPE, baka[num_img].image1)

	baka[num_img].typePrev = copy.deepcopy(baka[num_img].type1)
	baka[num_img].type2.part[0] = baka[num_img].type1.part[1]
	baka[num_img].type2.part[8] =  baka[num_img].type1.part[9]
	baka[num_img].type2.mode89 = True
	baka[num_img].image2, baka[num_img].type2 = produce_image(baka[num_img].image2, baka[num_img].type2, baka[num_img].typePrev)
	cv.imwrite(utils.OUTPUT_PATH + str(num_img) + 'B' + utils.OUTPUT_IMGTYPE, baka[num_img].image2)
	# cv.imwrite(utils.OUTPUT_PATH + utils.PROJ_NAME + format(num_img, '03d') + '/B' + utils.OUTPUT_IMGTYPE, baka[num_img].image2)
	
	baka[num_img].typePrev = copy.deepcopy(baka[num_img].type2)
	baka[num_img].type3.part[2] = baka[num_img].type2.part[2]
	baka[num_img].type3.part[4] = baka[num_img].type2.part[4]
	baka[num_img].type3.part[6] = baka[num_img].type2.part[6]
	# baka[num_img].type3.special = False
	baka[num_img].type3.mode89 = True
	baka[num_img].image3, baka[num_img].type3 = produce_image(baka[num_img].image3, baka[num_img].type3, baka[num_img].typePrev)
	cv.imwrite(utils.OUTPUT_PATH + str(num_img) + 'C' + utils.OUTPUT_IMGTYPE, baka[num_img].image3)
	# cv.imwrite(utils.OUTPUT_PATH + utils.PROJ_NAME + format(num_img, '03d') + '/C' + utils.OUTPUT_IMGTYPE, baka[num_img].image3)
	

