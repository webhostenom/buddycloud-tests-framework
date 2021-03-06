import string
from api_utils import *
from find_api_location import findAPILocation

MEMBER_USERNAME = "test_user_channel_follower4"
FOLLOWED_USER_CHANNELS = [ "test_user_channel_open", "test_user_channel_authorized" ]
FOLLOWED_TOPIC_CHANNEL = "test_topic_channel_open"

def testFunction(domain_url, session):

	CLASSIFIED = { 'SUBSCRIBED' : [],
		'PROBLEM_SUBSCRIBING_ASKING' : [],
		'PROBLEM_SUBSCRIBING_APPROVING' : [],
		'PROBLEM_CHANGING_SUBSCRIBER_ROLE' : [],
		'PROBLEM_DID_NOT_BAN' : [],
		'ALREADY_BANNED' : []}

	(status, briefing, message, api_location) = findAPILocation(domain_url)
	if status != 0:
		return (status, briefing, message, None)

	for followed_channel in FOLLOWED_USER_CHANNELS:

		if has_subscriber_role_in_user_channel(session, domain_url, api_location, MEMBER_USERNAME, followed_channel, "outcast"):
			CLASSIFIED['ALREADY_BANNED'].append(followed_channel + "@" + domain_url)
		else:

			if subscribe_to_user_channel(session, domain_url, api_location, MEMBER_USERNAME, followed_channel, "member"):
			
				if approve_user_channel_subscription_request(session, domain_url, api_location, followed_channel, [MEMBER_USERNAME]):

					if change_user_channel_subscriber_role(session, domain_url, api_location, followed_channel, MEMBER_USERNAME, "outcast"):

						if has_subscriber_role_in_user_channel(session, domain_url, api_location, MEMBER_USERNAME, followed_channel, "outcast"):
							CLASSIFIED['SUBSCRIBED'].append(followed_channel + "@" + domain_url)
						else:
							CLASSIFIED['PROBLEM_DID_NOT_BAN'].append(followed_channel + "@" + domain_url)

					else:
						CLASSIFIED['PROBLEM_CHANGING_SUBSCRIBER_ROLE'].append(followed_channel + "@" + domain_url)

				else:
					CLASSIFIED['PROBLEM_SUBSCRIBING_APPROVING'].append(followed_channel + "@" + domain_url)

			else:
				CLASSIFIED['PROBLEM_SUBSCRIBING_ASKING'].append(followed_channel + "@" + domain_url)

	for followed_channel in [FOLLOWED_TOPIC_CHANNEL]:

		if has_subscriber_role_in_topic_channel(session, domain_url, api_location, MEMBER_USERNAME, followed_channel, "outcast"):
			CLASSIFIED['ALREADY_BANNED'].append(followed_channel + "@" + domain_url)
		else:

			if subscribe_to_topic_channel(session, domain_url, api_location, MEMBER_USERNAME, followed_channel, "member"):
	
				if approve_topic_channel_subscription_request(session, domain_url, api_location, followed_channel, FOLLOWED_USER_CHANNELS[0], [MEMBER_USERNAME]):

					if change_topic_channel_subscriber_role(session, domain_url, api_location, FOLLOWED_USER_CHANNELS[0], MEMBER_USERNAME, followed_channel, "outcast"):

						if has_subscriber_role_in_topic_channel(session, domain_url, api_location, MEMBER_USERNAME, followed_channel, "outcast"):
							CLASSIFIED['SUBSCRIBED'].append(followed_channel + "@" + domain_url)
						else:
							CLASSIFIED['PROBLEM_DID_NOT_BAN'].append(followed_channel + "@" + domain_url)

					else:
						CLASSIFIED['PROBLEM_CHANGING_SUBSCRIBER_ROLE'].append(followed_channel + "@" + domain_url)

				else:
					CLASSIFIED['PROBLEM_SUBSCRIBING_APPROVING'].append(followed_channel + "@" + domain_url)

			else:
				CLASSIFIED['PROBLEM_SUBSCRIBING_ASKING'].append(followed_channel + "@" + domain_url)

	status = 0

	if ( ( len(CLASSIFIED.get('PROBLEM_SUBSCRIBING_ASKING', [])) > 0)
	or ( len(CLASSIFIED.get('PROBLEM_SUBSCRIBING_APPROVING', [])) > 0 )
	or ( len(CLASSIFIED.get('PROBLEM_CHANGING_SUBSCRIBER_ROLE', [])) > 0 )
	or ( len(CLASSIFIED.get('PROBLEM_DID_NOT_BAN', [])) > 0 ) ):

		problematic_channels = string.join(CLASSIFIED.get('PROBLEM_SUBSCRIBING_ASKING', []) + CLASSIFIED.get('PROBLEM_SUBSCRIBING_APPROVING', []) + CLASSIFIED.get('PROBLEM_CHANGING_SUBSCRIBER_ROLE', []) + CLASSIFIED.get('PROBLEM_DID_NOT_BAN', []), " | ")

		status = 1
		briefing = "Could not have some of these test channels promote <strong>%s@%s</strong> to <em>banned</em>: <br/><br/>" % (MEMBER_USERNAME, domain_url)
		briefing += "<strong>%s</strong>" % problematic_channels
		message = "Something weird happened while we tried having some test channels promote <strong>%s@%s</strong> to <em>banned</em> for testing purposes." % (MEMBER_USERNAME, domain_url)
		message += "<br/>The following test channels were problematic: <br/><br/>"
		message += "<strong>%s</strong>" % problematic_channels
		message += "<br/><br/>It seems like your HTTP API is problematic."

	else:

		briefing = "Could successfully have these test channels promote <strong>%s@%s</strong> to <em>banned</em> (that is, ban it), or assert it was already banned by these channels: " % (MEMBER_USERNAME, domain_url)
		briefing += "<strong>%s</strong>" % string.join(CLASSIFIED.get('SUBSCRIBED', []) + CLASSIFIED.get('ALREADY_BANNED', []), " | ")
		message = "We could assert that these user channels which will be used later for testing purposes"
		message += " could successfully promote <strong>%s@%s</strong> to <em>banned</em> (that is, ban it):" % (MEMBER_USERNAME, domain_url)
		message += "<br/><br/><strong>%s</strong>" % string.join(CLASSIFIED.get('SUBSCRIBED', []) + CLASSIFIED.get('ALREADY_BANNED', []), "<br/>")

	return (status, briefing, message, None)
