import dns.resolver
from sleekxmpp import ClientXMPP


def testFunction(domain_url):

	answers = []
	query_for_SRV_record = None

	try:

		query_for_SRV_record = dns.resolver.query("_xmpp-server._tcp."+domain_url, dns.rdatatype.SRV)

	except dns.resolver.NXDOMAIN:
	
		briefing = "No XMPP server SRV record found at domain "+domain_url+"!"
		status = 1
		message = "We were unable to find your XMPP server. Check at http://buddycloud.org/wiki/Install#DNS on how to setup the DNS for your domain."
		return (status, briefing, message, None)

	except Exception, e:
	
		briefing = "A problem happened while searching for a XMPP server SRV record!"
		status = 2
		message = "Something odd happened while we were looking a XMPP server SRV record up at your domain at "+domain_url+": "+str(e)+". "
		message += "<br/>It could be a bug in our Inspector. Let us know at <email> if you think so." 
		return (status, briefing, message, None)

	for answer in query_for_SRV_record:

		try:

			domain = answer.target.to_text()[:-1]
			port = str(answer.port)

			answers.append({
				'domain' : domain,
				'port' : port,
				'priority' : answer.priority,
				'weight' : answer.weight
			})

		except Exception, e:
			continue

	if len(answers) == 0:
		
		briefing = "XMPP server SRV record found at domain "+domain_url+" but it doesn't contain all the relevant information!"
		status = 1
		message = "We were unable to find your XMPP server, even though we could find your XMPP SRV record."
		message += "<br/>Check at http://buddycloud.org/wiki/Install#DNS on how to setup the DNS for your domain."
		return (status, briefing, message, None)

	else:

		found = answers[0]['domain'] + ", port: " + str(answers[0]['port'])

		for i in range(1, len(answers)):
			found += " | " + answers[i]['domain'] + ", port: " + str(answers[i]['port'])

		if len(answers) == 1:
			found = "XMPP server SRV record found: " + found
		else:
			found = "XMPP server SRV records found: " + found

		briefing = found
		status = 0
		message = "You have said that the following addresses will handle all XMPP messages for this domain.<br/>"
		message += briefing
		return (status, briefing, message, answers)

