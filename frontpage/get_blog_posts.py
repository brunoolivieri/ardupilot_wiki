#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Script to get last blog entries on Discourse (https://discuss.ardupilot.org/)

'''
import argparse
import urllib.request
import json
import sys
import os
import re

parser = argparse.ArgumentParser(description="python3 get_blog_posts.py [Number of posts to retrive]")
parser.add_argument("--n_posts", dest='n_posts', default="8", help="Number of posts to retrive")
parser.add_argument('--verbose', dest='verbose', action='store_false', default=True, help="show debugging output")
args = parser.parse_args()

BLOG_DISCOURSEURL = "https://discuss.ardupilot.org/c/blog/110.json"
NEWS_DISCOURSEURL = "https://discuss.ardupilot.org/latest.json"
files_names = {BLOG_DISCOURSEURL:'blog_posts.json', NEWS_DISCOURSEURL:'news_posts.json'} 
error_count = 0


def clean_html(raw_html):
  cleanr = re.compile('<.*?>')
  clean_text = re.sub(cleanr, '', raw_html)
  return clean_text


def debug(str_to_print):
    """ Debug output if verbose is set. """
    if args.verbose:
        print("[get_blog_posts.py] " + str(str_to_print))


def error(str_to_print):
    """ Show and count the errors. """

    global error_count
    error_count += 1
    print("[get_discourse_posts.py][error]: " + str(str_to_print))


def get_posts(url):
    """ Download Discourse last posts page in JSON format. """

    try:
        request = urllib.request.Request(url)
        request = urllib.request.urlopen(request).read()
        content = json.loads(request.decode('utf-8'))
    except Exception as e:
        error(e)
        sys.exit(1)
    finally:
        return content


def get_single_post_text(url):
    """ Download Discourse specific post in JSON format. """

    try:
        request = urllib.request.Request(url)
        request = urllib.request.urlopen(request).read()
        content = json.loads(request.decode('utf-8'))
    except Exception as e:
        error(e)
        sys.exit(1)
    finally:
        post_text =  clean_html(str(content['post_stream']['posts'][0]['cooked'])) 
        # removing \n on the text
        item = post_text.split('\n')
        item = " ".join(item)
        # TO-DO: removing multiple white spaces due the \n removal
        #
        # returning twitter style string
        return str(item[0:140] +  ' (...)')


def save_posts_to_json(url):
    """ Save last N posts from blog to the JSON file. """

    content = get_posts(url)
    data =[]
    for i in range(1, int(args.n_posts) + 1):
        item = content['topic_list']['topics'][i]
        single_post_link = str('https://discuss.ardupilot.org/t/' + str(item['slug']) + 
                    '/' + str(item['id']))
        single_post_text = get_single_post_text(single_post_link + '.json')
        data.append({'title':item['title'], 'image':item['image_url'], 
                    'link':single_post_link, 'text':single_post_text })
    try:
        target_file = os.path.join(os.getcwd(), files_names[url])
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        error(e)
        sys.exit(1)



save_posts_to_json(BLOG_DISCOURSEURL)
save_posts_to_json(NEWS_DISCOURSEURL)

