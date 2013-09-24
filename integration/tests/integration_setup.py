from requests import Request, Session
from random import random
import json, base64

#util_dependencies
from domain_name_lookup import testFunction as domainNameLookup
from ssl_adapter import SSLAdapter

#installation_suite_dependencies
from api_server_lookup import testFunction as apiLookup
from api_server_connection import testFunction as apiConnection


TEST_USERNAMES = [ "1st_test_user", "2nd_test_user", "3rd_test_user", "4th_test_user", "5th_test_user" ]
TEST_USER_EMAIL = 'some@email.com'
TEST_USER_PASSWORD = 'a-password' #Those are not actually used for authentication
TEST_CHANNEL_NAME = "test_topic_channel"

def user_exists(domain_url, api_location, username):

	headers = {
		'Accept' : '*/*',
		'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4',
		'Cache-Control' : 'no-cache',
		'Connection' : 'keep-alive',
	}

	req = Request('GET', api_location + username +'@' + domain_url + '/metadata/posts', headers=headers)
	r = req.prepare()

	s = Session()
	s.mount('https://', SSLAdapter('TLSv1'))

	if (s.send(r, verify=False)).ok :
		return True
	return False

def create_user_channel(domain_url, api_location, username):

	if user_exists(domain_url, api_location, username):
		return True

	headers = {
		'Content-Type' : 'application/json',
		'Accept' : '*/*',
		'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4',
		'Cache-Control' : 'no-cache',
		'Connection' : 'keep-alive',
	}
	data = {'username' : username, 'password' : TEST_USER_PASSWORD, 'email' : TEST_USER_EMAIL}

	req = Request('POST', api_location + 'account', data=json.dumps(data), headers=headers)
	r = req.prepare()
	
	s = Session()
	s.mount('https://', SSLAdapter('TLSv1'))

	if (s.send(r, verify=False)).ok :
		return True
	return False

def topic_channel_exists(domain_url, api_location, channel_name):

	headers = {
		'Accept' : '*/*',
		'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4',
		'Cache-Control' : 'no-cache',
		'Connection' : 'keep-alive',
	}
	
	req = Request('GET', api_location + channel_name +'@topics.' + domain_url + '/metadata/posts', headers=headers)
	r = req.prepare()

	s = Session()
	s.mount('https://', SSLAdapter('TLSv1'))

	if (s.send(r, verify=False)).ok :
		return True
	return False

def create_topic_channel(domain_url, api_location, username, channel_name):

	if topic_channel_exists(domain_url, api_location, channel_name):
		return True

	headers = {
		'Content-Type' : 'application/json',
		'Accept' : '*/*',
		'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4',
		'Cache-Control' : 'no-cache',
		'Connection' : 'keep-alive',
		'Authorization' : 'Basic ' + base64.b64encode(username+":"+TEST_USER_PASSWORD)
	}

	req = Request('POST', api_location + channel_name + "@topics." + domain_url + "", headers=headers)
	r = req.prepare()

	s = Session()
	s.mount("https://", SSLAdapter("TLSv1"))

	if (s.send(r, verify=False)).ok :

		data = {
			"default_affiliation": "member"
		}

		req = Request('POST', api_location + channel_name + "@topics." + domain_url + "/metadata/posts", data=json.dumps(data), headers=headers)
		r = req.prepare()

		s = Session()
		s.mount("https://", SSLAdapter("TLSv1"))

		if (s.send(r, verify=False)).ok :
			return True
	return False

def subscribe_to_channel(domain_url, api_location, username, channel_name, subscription):

	headers = {
		'Accept' : '*/*',
		'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4',
		'Cache-Control' : 'no-cache',
		'Connection' : 'keep-alive',
		'Content-Type' : 'application/json',
		'Authorization' : 'Basic ' + base64.b64encode(username+":"+TEST_USER_PASSWORD)
	}

	data = {
		channel_name + "@topics." + domain_url + "/posts" : subscription
	}

	req = Request('POST', api_location + "subscribed", data=json.dumps(data), headers=headers)
	r = req.prepare()

	s = Session()
	s.mount("https://", SSLAdapter("TLSv1"))

	if (not s.send(r, verify=False).ok):
		status = 1
		briefing = "User " + username + "@" + domain_url + " could not subscribe to topic channel named " + channel_name + "@topics." + domain_url + "."
		message = briefing
		return (status, briefing, message, None)

def is_subscribed_to_channel(domain_url, api_location, username, channel_name, subscription):

	headers = {
		'Accept' : '*/*',
		'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4',
		'Cache-Control' : 'no-cache',
		'Connection' : 'keep-alive',
		'Authorization' : 'Basic ' + base64.b64encode(username+":"+TEST_USER_PASSWORD)
	}

	req = Request('GET', api_location + "subscribed", headers=headers)
	r = req.prepare()

	s = Session()
	s.mount("https://", SSLAdapter("TLSv1"))

	resp = s.send(r, verify=False)

	if (not resp.ok):

		status = 1
		briefing = "Could not assert that user " + username + "@" + domain_url + " is subscribed:'" + subscription + "' of topic channel named " + channel_name + "@topics." + domain_url + "."
		message = briefing
		return (status, briefing, message, None)
	else:

		resp = json.loads(resp.content)

		if (not (channel_name + "@topics." + domain_url + "/posts") in resp) or (resp[(channel_name + "@topics." + domain_url + "/posts")] != subscription):
			status = 1
			briefing = "Problem: " + username + "@" + domain_url + " is not subscribed:'" + subscription + "' of topic channel named " + channel_name + "@topics." + domain_url + "."
			message = briefing
			return (status, briefing, message, None)
		else:
			status = 0
			briefing = username + "@" + domain_url + " is subscribed:'" + subscription + "' of topic channel named " + channel_name + "@topics." + domain_url + "!"
			message = briefing
			return (0, briefing, message, None)

def change_subscriber_role(domain_url, api_location, owner_username, username, channel_name, subscription):

	headers = {
		'Accept' : '*/*',
		'Accept-Encoding' : 'gzip,deflate,sdch',
		'Accept-Language' : 'en-US,en;q=0.8,pt-BR;q=0.6,pt;q=0.4',
		'Cache-Control' : 'no-cache',
		'Connection' : 'keep-alive',
		'Authorization' : 'Basic ' + base64.b64encode(owner_username+":"+TEST_USER_PASSWORD)
	}

	data = {
		username + "@" + domain_url : subscription
	}

	req = Request('POST', api_location + channel_name + "@topics." + domain_url + "/subscribers/posts", data=json.dumps(data), headers=headers)
	r = req.prepare()

	s = Session()
	s.mount("https://", SSLAdapter("TLSv1"))

	resp = s.send(r, verify=False)

	if (not resp.ok):

		status = 1
		briefing = "Onwer (%s) of channel (%s) could not promote subscriber (%s) to %s." % (owner_username + "@" + domain_url, channel_name, username + "@" + domain_url, subscription)
		message = briefing
		return (0, briefing, message, None)

def testFunction(domain_url):

	(status, briefing, message, output) = domainNameLookup(domain_url)
	if ( status != 0 ):
		return (status, briefing, message, None)

	#First of all, let's find the API server

	status, briefing, message, data = apiLookup(domain_url)
	if ( status != 0 ):
		status = 2
		briefing = "This test was skipped because previous test <strong>api_server_lookup</strong> has failed.<br/>"
		new_message = briefing
		new_message += "Reason:<br/>"
		new_message += "<br/>" + message
		return (status, briefing, new_message, None)

	status, briefing, message, output = apiConnection(domain_url)
	if ( status != 0 ):
		status = 2
		briefing = "This test was skipped because previous test <strong>api_server_connection</strong> has failed.<br/>"
		new_message = briefing
		new_message = "Reason:<br/>"
		new_message += "<br/>" + message
		return (status, briefing, new_message, None)

	api_location = "%(protocol)s://%(domain)s%(path)s/" % data

	# Then, create a user channel for each of the test usernames, if that does not exist yet.

	for test_username in TEST_USERNAMES:

		test_username = test_username.strip()

		if create_user_channel(domain_url, api_location, test_username):
			continue
		else:
			status = 1
			briefing = "Could not create user channel for test user named " + test_username + "@" + domain_url + "."
			message = briefing
			return (status, briefing, message, None)


	# Then, have user[1] create a topics channel. Assert he is the owner of that channel.

	if not create_topic_channel(domain_url, api_location, TEST_USERNAMES[0], TEST_CHANNEL_NAME) :
		status = 1
		briefing = "Could not create topic channel named " + TEST_CHANNEL_NAME + "@topics." + domain_url + "."
		message = briefing
		return (status, briefing, message, None)

	output = is_subscribed_to_channel(domain_url, api_location, TEST_USERNAMES[0], TEST_CHANNEL_NAME, "owner")
	if ( output[0] != 0 ):
		return output

	# Then, have user[2] join the topic channel. Have user[1] make user[2] moderator of that channel. Assert user[2] is a moderator of that channel.	

	subscribe_to_channel(domain_url, api_location, TEST_USERNAMES[1], TEST_CHANNEL_NAME, "publisher")
	change_subscriber_role(domain_url, api_location, TEST_USERNAMES[0], TEST_USERNAMES[1], TEST_CHANNEL_NAME, "moderator")
	output = is_subscribed_to_channel(domain_url, api_location, TEST_USERNAMES[1], TEST_CHANNEL_NAME, "moderator")
	if ( output[0] != 0 ):
		return output

	#TODO see how to promote test_user[1] to moderator (and not only a producer!!)

	# Then, have user[3] join the topic channel. Have user[1] give posting permission to user[3]. Assert user[3] is a follower+post of that channel.

	subscribe_to_channel(domain_url, api_location, TEST_USERNAMES[2], TEST_CHANNEL_NAME, "publisher")
	change_subscriber_role(domain_url, api_location, TEST_USERNAMES[0], TEST_USERNAMES[2], TEST_CHANNEL_NAME, "publisher")
	output = is_subscribed_to_channel(domain_url, api_location, TEST_USERNAMES[2], TEST_CHANNEL_NAME, "publisher")
	if ( output[0] != 0 ):
		return output

	# Then, have user[4] join the topic channel. Assert user[4] is a follower of that channel.

	subscribe_to_channel(domain_url, api_location, TEST_USERNAMES[3], TEST_CHANNEL_NAME, "member")
	output = is_subscribed_to_channel(domain_url, api_location, TEST_USERNAMES[3], TEST_CHANNEL_NAME, "member")
	if ( output[0] != 0 ):
		return output

	# Then, have user[5] join the topic channel. Have user[1] ban user[5] in that channel. Assert user[5] is banned in that channel.

	subscribe_to_channel(domain_url, api_location, TEST_USERNAMES[4], TEST_CHANNEL_NAME, "member")
	change_subscriber_role(domain_url, api_location, TEST_USERNAMES[0], TEST_USERNAMES[4], TEST_CHANNEL_NAME, "outcast")
	output = is_subscribed_to_channel(domain_url, api_location, TEST_USERNAMES[4], TEST_CHANNEL_NAME, "outcast")
	if ( output[0] != 0 ):
		return output

	#TODO have this user TEST_USERNAMES[4]@buddycloud.org be banned from this topic channel TEST_CHANNEL_NAME@topics.buddycloud.org

	briefing = "Integration test suite setup procedures executed properly. Ready to run integration tests."
	message = briefing
	message += "<br/>Could successfully create all test user channels and topic channels needed for incoming integration tests."
	return (status, briefing, message, None)
