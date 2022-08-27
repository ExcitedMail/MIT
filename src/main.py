#-*- coding: utf-8 -*-

import cv2 as cv
import cvzone
import sys
import time
import copy
import numpy as np
import utils
import glob
import os
import json
from tqdm import trange
from random import randint


import BAKA


# Create 2D list to store parts
list_image_hash = []
basic_files = []
special_files = []

# Create image hash for opencv
hsh = cv.img_hash.BlockMeanHash_create()
# hsh.compute(a_1)
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

	

	# initialize background
	is_duplicate = True
	while(is_duplicate == True):
		
		part_backup = copy.deepcopy(current_part)

		# set if body is special
		if(current_part.mode89 == False and randint(0, 10) < 2):
			# print('special!!')
			current_part.special = True
		else:
			current_part.special = False
	
		b, g, r = randint(0, 256), randint(0, 256), randint(0, 256)
		current_image[:] = (b, g, r)
		image_for_hash = np.zeros((utils.HEIGHT, utils.WIDTH, 3), np.uint8)


		# get random file parts if body special
		if(current_part.special):
			current_index = [1, 3, 5, 7, 9]
			# choose body			
			rand_num = randint(0, len(special_files[0])-1)
			part = cv.imread(special_files[0][rand_num], cv.IMREAD_UNCHANGED)
			current_part.part[1] = special_files[0][rand_num]
			current_image = cvzone.overlayPNG(current_image, part, [0, 0])
			image_for_hash = cvzone.overlayPNG(image_for_hash, part, [0, 0])
			
			# get transparent hand
			part = cv.imread(special_files[1][0], cv.IMREAD_UNCHANGED)
			current_part.part[9] = special_files[1][0]
			current_image = cvzone.overlayPNG(current_image, part, [0, 0])
			image_for_hash = cvzone.overlayPNG(image_for_hash, part, [0, 0])
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
			image_for_hash = cvzone.overlayPNG(image_for_hash, part, [0, 0])
		
		hash_value = hsh.compute(image_for_hash)
		hash_value = list(hash_value[0])
		# print(hash_value, list_image_hash)
		# print(type(hash_value), type(list_image_hash))
		if(hash_value in list_image_hash):
			current_part = copy.deepcopy(part_backup)
			print('duplicate happen!!')
			is_duplicate = True
		else:
			list_image_hash.append(list(hash_value))
			is_duplicate = False
		# is_duplicate = False

	return current_image, current_part

		
def pack_to_json(current_num, current_baka):
	# name, id: name or hash, description: maybe fix string, url_ipfs: remain empty, base64: img to base64, part attribute
	d_1 = {
		'name' : utils.PROJ_NAME + format(current_num, '03d') + 'A',
		'base64': '',
		'url_mongo': '',
		'url_iftp': '',
	}
	d_2 = {
		'name' : utils.PROJ_NAME + format(current_num, '03d') + 'B',
		'url_mongo': '',
		'url_iftp': '',
	}
	d_3 = {
		'name' : utils.PROJ_NAME + format(current_num, '03d') + 'C',
		'url_mongo': '',
		'url_iftp': '',
	}
	return d_1, d_2, d_3


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

	dic = pack_to_json(num_img, baka[num_img])
	# Serializing json
	json_list = [0]*3
	for i in range(3):
		json_list[i] = json.dumps(dic[i], indent=4)
		
		# Writing to sample.json
		with open(utils.OUTPUT_PATH + utils.PROJ_NAME + format(num_img, '03d') + format(i, '01d'), 'w') as outfile:
			outfile.write(json_list[i])
