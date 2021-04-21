#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2021

@author: kanarinka
"""

import instaloader
from datetime import datetime
import json
import csv
import time
from progress.bar import IncrementalBar

################################
# PUT YOUR OWN VALUES HERE

# Username of account you will use for logging in
USER = "kanarinkaprojects"

# Hashtag that you want to download IG posts from
HASHTAG_TO_SEARCH = "culturalemergency"

# Limit of posts to download. Limit to 10 or 20 while
# testing or else it'll take forever. Set to -1 to get
# everything.
LIMIT = 5

################################

# Set up Instaloader instance
L = instaloader.Instaloader()
L.interactive_login(USER)

# Set up CSV file & header row
current_time = datetime.now().strftime("%m%d%Y-%H%M%S")

fname = HASHTAG_TO_SEARCH +'-output-' + current_time +'.csv'
csvFile = open(fname, 'w', encoding="utf-8-sig")

fieldnames = [
				'shortcode',
				'mediaid',
				'title',
				'owner_username',
				'owner_id',
				'date_local',
				'date_utc',
				'url',
				'mediacount',
				'caption',
				'caption_hashtags',
				'caption_mentions',
				'tagged_users',
				'is_video',
				'video_url',
				'video_view_count',
				'video_duration',
				'likes',
				'comment_count',
				'users_who_commented',
				'all_comments_text',
				'is_sponsored',
				'location_id',
				'location_lat',
				'location_lng',
				'location_name'
			 ]
csvWriter = csv.DictWriter(csvFile, fieldnames=fieldnames, dialect="excel")
csvWriter.writeheader()


# Retrieve hashtag object

# Uncomment this after issue #1080 is fixed
# hashtag = instaloader.Hashtag.from_name(L.context, HASHTAG_TO_SEARCH)
# print("Retrieved hashtag " + hashtag.name)
# print("Hashtag #" + hashtag.name + " has " + str(hashtag.mediacount) + " items ")
# post_count = hashtag.mediacount

# in the meantime, use this workaround specified in issue #874
post_iterator = instaloader.NodeIterator(
    L.context, "9b498c08113f1e09617a1703c22b2f32",
    lambda d: d['data']['hashtag']['edge_hashtag_to_media'],
    lambda n: instaloader.Post(L.context, n),
    {'tag_name': HASHTAG_TO_SEARCH},
    f"https://www.instagram.com/explore/tags/{HASHTAG_TO_SEARCH}/"
)

print("Retrieved hashtag " + HASHTAG_TO_SEARCH)
print("Hashtag #" + HASHTAG_TO_SEARCH + " has " + str(post_iterator.count) + " items ")
post_count = post_iterator.count
# end workaround


# set up progress bar because this takes awhile
bar = IncrementalBar('Countdown', max = post_count)

if LIMIT > 0:
	print("Limiting download to " + str(LIMIT) + " posts for testing")
	bar = IncrementalBar('Countdown', max = min(LIMIT, post_count))


# Iterate each post and save media to disk + metadata to spreadsheet
# for post in hashtag.get_posts():
# WORKAROUND WITH POST ITERATOR
for post in post_iterator:
	# Download the media and metadata as JSON
	L.download_post(post, target="#"+HASHTAG_TO_SEARCH)

	# Format comments for including in CSV
	all_comments = post.get_comments()
	users_who_commented = []
	all_comments_text = []

	for comment in all_comments:
		users_who_commented.append(comment.owner.username)
		comment_text = str(json.loads(json.dumps(comment.text)))
		all_comments_text.append(comment_text)

	# Format caption
	caption_text = str(json.loads(json.dumps(post.caption)))

	# Handle null location objects
	if post.location is None:
		post_location_id = ""
		post_location_lat = ""
		post_location_lng = ""
		post_location_name = ""
	else:
		post_location_id = post.location.id
		post_location_lat = post.location.lat
		post_location_lng = post.location.lng
		post_location_name = post.location.name

	# Assemble the row in the CSV
	row = {
		'shortcode': post.shortcode,
		'mediaid': post.mediaid,
		'title': post.title,
		'owner_username': post.owner_username,
		'owner_id': post.owner_id,
		'date_local': post.date_local.strftime("%x %X"),
		'date_utc': post.date_utc.strftime("%x %X"),
		'url': post.url,
		'mediacount': post.mediacount,
		'caption': caption_text,
		'caption_hashtags': ' '.join([str(elem) for elem in post.caption_hashtags]),
		'caption_mentions': ' '.join([str(elem) for elem in post.caption_mentions]),
		'tagged_users': ' '.join([str(elem) for elem in post.tagged_users]),
		'is_video': post.is_video,
		'video_url': post.video_url,
		'video_view_count': post.video_view_count,
		'video_duration': post.video_duration,
		'likes': post.likes,
		'comment_count': post.comments,
		'users_who_commented':' '.join([str(elem) for elem in users_who_commented]),
		'all_comments_text': ' @@@ '.join([str(elem) for elem in all_comments_text]),
		'is_sponsored': post.is_sponsored,
		'location_id': post_location_id,
		'location_lat': post_location_lat,
		'location_lng': post_location_lng,
		'location_name': post_location_name
	}
	
	# Write the row into the CSV file
	csvWriter.writerow(row)
	bar.next()
	
	# Break if LIMIT of posts has been reached
	if LIMIT > 0:
		LIMIT -= 1
	if LIMIT == 0: 
		break

#Clean up
bar.finish()
csvFile.close()
print("Success! Created file " + fname)


