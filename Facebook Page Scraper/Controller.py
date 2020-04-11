from FacebookScraper import Scraper
import pandas as pd
import time

page_sheet_columns = ['# page likes', '# page followers']
post_sheet_columns = ['status_id', 'status_message', 'status_type', 'status_published',
                      'num_reactions', 'num_comments', 'num_shares',
                      'num_likes', 'num_loves', 'num_wows', 'num_hahas', 'num_sads', 'num_angrys']
like_sheet_columns = ['status_id', "user_id", "user_network_size", "user_network", "Follower", "Degree"]
share_sheet_columns = ['status_id', "share_published_time", "user_id", "user_network_size", "user_network", "Follower",
                       "Degree",
                       "#likes on shares", "#followers on likes", "#not followers on likes",
                       '#comments on shares', '#followers on comments', '#not followers on comments',
                       "#shares on shares", "#followers on shares", "#not followers on shares"]
comment_sheet_columns = ['page_id','comment_id', 'status_id', 'parent_id',
                         'comment_message',
                         'comment_author', '#author network', 'author network', 'Follower', "Degree",
                         'comment_published',
                         '#comment_likes', '#followers in likes', '# not followers in likes',
                         '#comment replies', '# followers in replies', '#not followers in replies']


def list_to_string(list_data, default):
    if len(list_data) == 0:
        return default
    return ', '.join('"{0}"'.format(w) for w in list_data)


def get_post_list(page_title):
    post_data_list = scraper.get_post_list(page_title)
  #  post_data_template = {'page_id': '', 'post_id': '', 'post_type': '', 'post_published': '',
  #                            'num_shares': 0, 'num_comments': 0}
    for post_data in post_data_list:
        post_link = "https://m.facebook.com/{}/posts/{}".format(post_data['page_id'], post_data['post_id'])
        post_details = scraper.get_post_details(post_link)
        #post_details = {'post_message': '', 'post_like_link': '', 'post_share_link': ''}
        post_data.update(post_details)
        
        reactions_data = scraper.get_reactions_count(post_data['post_like_link'])
     #  reactions = {'All': 0, 'Like': 0, 'Wow': 0, 'Love': 0, 'Haha': 0, 'Sad': 0, 'Angry': 0,}
        post_data.update(reactions_data)
    return post_data_list


def generate_page_sheet(pagename):
    page_data = scraper.get_page_data(pagename)
    data_frame = pd.DataFrame(columns=page_sheet_columns)
    data_frame.loc[1] = [page_data['page_likes'], page_data['page_followers']]
    data_frame.to_excel(writer, "Page", index=False)
    writer.save()


def generate_post_sheet_data_frame(post_data):
    # make sure below columns are in sync with post_sheet_columns
    columns = ['post_id', 'post_message', 'post_type', 'post_published',
               'All', 'num_comments', 'num_shares',
               'Like', 'Wow', 'Love', 'Haha', 'Sad', 'Angry']
    if len(post_sheet_columns) != len(columns):
        raise Exception
    data = []
    for column in columns:
        data.append(post_data[column])
    return data


def generate_post_sheet(post_data_list):
    data_frame = pd.DataFrame(columns=post_sheet_columns)
    for index, post_data in enumerate(post_data_list):
        data_frame.loc[index + 1] = generate_post_sheet_data_frame(post_data)
    data_frame.to_excel(writer, "Post", index=False)
    writer.save()


def generate_like_sheet_data_frame(post_id, user, user_network, page_follower, degree):
    user_network_size = len(user_network)
    user_network = list_to_string(user_network, "Private")
    return [post_id, user, user_network_size, user_network, page_follower, degree]


def generate_share_sheet_data_frame(post_id, user, user_network, page_follower, degree, num_likes_on_shares,
                                    num_followers_in_likes_on_shares, num_shares_on_shares,
                                    num_followers_in_shares_on_shares, share_published_time):
    user_network_size = len(user_network)
    user_network = list_to_string(user_network, "Private")
    return [post_id, share_published_time, user, user_network_size, user_network, page_follower, degree,
            num_likes_on_shares, num_followers_in_likes_on_shares,
            num_likes_on_shares - num_followers_in_likes_on_shares,
            0, 0, 0,
            num_shares_on_shares, num_followers_in_shares_on_shares,
            num_shares_on_shares - num_followers_in_shares_on_shares]


def generate_like_sheet(post_data_list):
    data_frame = pd.DataFrame(columns=like_sheet_columns)
    index = 0
    for post_data in post_data_list:
        liked_user_list = scraper.get_liked_user_list(post_data['post_like_link'])
        for liked_user in liked_user_list:
            # Get User Network
            user_network = get_user_network(liked_user)
            # Check If user is a follower of page
            if is_user_a_follower_of_page(liked_user, post_data['page_id']):
                is_user_page_follower = 1
                degree = 1
            else:
                is_user_page_follower = 0
                degree = 2
            # Generate Excel Sheet Row
            data_frame.loc[index + 1] = \
                generate_like_sheet_data_frame(post_data['post_id'], liked_user, user_network, is_user_page_follower,
                                               degree)
            index += 1
    data_frame.to_excel(writer, "Like", index=False)
    writer.save()


def is_user_a_follower_of_page(user_id, page_id):
    if len(user_id) == 0:
        return False
    if user_id in user_liked_pages_cache:
        user_liked_pages = user_liked_pages_cache[user_id]
    else:
        username = scraper.get_username_from_user_id(user_id)
        user_liked_pages = scraper.get_user_data(username, "liked_pages")
        user_liked_pages_cache[user_id] = user_liked_pages
    if page_id in user_liked_pages:
        return True
    else:
        return False


def get_user_network(user_id):
    if len(user_id) == 0:
        return []
    if user_id in user_network_cache:
        network = user_network_cache[user_id]
    else:
        network = scraper.get_user_data(user_id, "network")
        user_network_cache[user_id] = network
    return network


def generate_share_sheet(post_data_list):
    data_frame = pd.DataFrame(columns=share_sheet_columns)
    index = 0
    for post_data in post_data_list:
        share_data_list = scraper.get_shared_user_list(post_data['post_share_link'], False)
        for share_data in share_data_list:
            share_published_time = share_data['published_time']
            shared_user = share_data['user_id']
            # Get Network of Shared User
            user_network = get_user_network(shared_user)
            # Check if shared_user is a follower of page
            if is_user_a_follower_of_page(shared_user, post_data['page_id']):
                is_user_page_follower = 1
                degree = 1
            else:
                is_user_page_follower = 0
                degree = 2
            # Get number of Likes on share, number of followers of page in liked users
            share_liked_user_list = scraper.get_liked_user_list(share_data['like_link'])
            num_of_users_liked_the_share = len(share_liked_user_list)
            num_of_page_followers_in_share_liked_users = 0
            for share_liked_user in share_liked_user_list:
                if is_user_a_follower_of_page(share_liked_user, post_data['page_id']):
                    num_of_page_followers_in_share_liked_users += 1
            # Get number of Shares on share, number of followers of page in shared users
            share_shared_data_list = scraper.get_shared_user_list(share_data['share_link'], True)
            num_of_users_shared_the_share = len(share_shared_data_list)
            num_of_page_followers_in_share_shared_users = 0
            for share_shared_data in share_shared_data_list:
                share_shared_user = share_shared_data['user_id']
                if is_user_a_follower_of_page(share_shared_user, post_data['page_id']):
                    num_of_page_followers_in_share_shared_users += 1
            # Generate a Excel Sheet Row
            data_frame.loc[index + 1] = \
                generate_share_sheet_data_frame(post_data['post_id'], shared_user, user_network, is_user_page_follower,
                                                degree, num_of_users_liked_the_share,
                                                num_of_page_followers_in_share_liked_users,
                                                num_of_users_shared_the_share,
                                                num_of_page_followers_in_share_shared_users, share_published_time)
            index += 1
    data_frame.to_excel(writer, "Share", index=False)
    writer.save()

"""
def generate_comment_sheet_data_frame(page_id, comment_id, post_id, parent_id,
                                      comment_msg,
                                      comment_author, author_network,
                                      comment_liked_users, comment_replied_users, post_commented_time):
    follower = 0
    degree = 2
    if is_user_a_follower_of_page(comment_author, page_id):
        follower = 1
        degree = 1
    num_of_comment_likes = len(comment_liked_users)
    num_of_followers_in_likes = 0
    for comment_liked_user in comment_liked_users:
        if is_user_a_follower_of_page(comment_liked_user, page_id):
            num_of_followers_in_likes += 1
    num_of_comment_replies = len(comment_replied_users)
    num_of_followers_in_replies = 0
    for comment_replied_user in comment_replied_users:
        if is_user_a_follower_of_page(comment_replied_user, page_id):
            num_of_followers_in_replies += 1
    return [comment_id, post_id, parent_id,
            comment_msg,
            comment_author, len(author_network), list_to_string(author_network, "Private"), follower, degree,
            post_commented_time,
            num_of_comment_likes, num_of_followers_in_likes, num_of_comment_likes - num_of_followers_in_likes,
            num_of_comment_replies, num_of_followers_in_replies, num_of_comment_replies - num_of_followers_in_replies]     
"""


def generate_comment_sheet_data_frame(page_id, comment_id, post_id, parent_id,
                                      comment_msg,
                                      comment_author, author_network,
                                      comment_liked_users, comment_replied_users, post_commented_time):
    print("\ngenerate comments sheet data frame called")
    num_of_comment_likes = len(comment_liked_users)
    num_of_comment_replies = len(comment_replied_users)
    return [page_id, comment_id, post_id, parent_id,
            comment_msg,
            comment_author, '', '', '', '',
            post_commented_time,
            num_of_comment_likes, '','',
            num_of_comment_replies, '','' ]     


def generate_comments_sheet(post_data_list):
    print("\ngenerate comments sheet called")
    data_frame = pd.DataFrame(columns=comment_sheet_columns)
    index = 0
    for post_data in post_data_list:
        page_id = post_data['page_id']
        post_id = post_data['post_id']
        post_comment_data_list = scraper.get_post_comments_data(page_id, post_id)
        for post_comment_data in post_comment_data_list:
            
            comment_author_id = post_comment_data['comment_author'] 
            print("\n"+comment_author_id)
          #  comment_author_id = scraper.get_user_id_from_username(post_comment_data['comment_author'])
         #   comment_author_network = get_user_network(comment_author_id)
         #   comment_liked_user_list = scraper.get_liked_user_list(post_comment_data['comment_like_link'])
         #   comment_replied_user_list = post_comment_data['reply_username_list']
         #   for user_index, comment_replied_user in enumerate(comment_replied_user_list):
         #       comment_replied_user_id = scraper.get_user_id_from_username(comment_replied_user)
         #       comment_replied_user_list[user_index] = comment_replied_user_id
            data_frame.loc[index + 1] = \
                generate_comment_sheet_data_frame(page_id,
                                                  post_comment_data['comment_id'], post_id,
                                                  post_comment_data['parent_id'],
                                                  post_comment_data['comment_message'],
                                                  comment_author_id,'',
                                                  '', '',
                                                  post_comment_data['comment_time'])
            index += 1
    data_frame.to_excel(writer, "Comment", index=False)
    writer.save()


user_network_cache = {}
user_liked_pages_cache = {}
print("Please login to your facebook account")
user_name = input("Username:  ")
password = input("Password:  ")
page_name = input("Enter page name (if page link is like https://www.facebook.com/NASA/, then enter only NASA): ")
#user_name = ""
#password = ""
#page_name = ""
output_file_name = "facebook_{}.xlsx".format(page_name)
writer = pd.ExcelWriter(output_file_name)
scraper = Scraper(user_name, password)
post_list = get_post_list(page_name)
#generate_page_sheet(page_name)
#generate_post_sheet(post_list)
#generate_like_sheet(post_list)
#generate_share_sheet(post_list)
generate_comments_sheet(post_list)
scraper.close()
