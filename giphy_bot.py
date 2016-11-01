from itty import *
import urllib2
import json

giphy_API = 'dc6zaTOxFJmzC'

def giphyGET(url):
    """
    This method is used for:
        -retrieving GIF URL from Giphy
    """
    print "url giphy",  url
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    contents = urllib2.urlopen(request).read()
    print contents
    return contents

def sendSparkGET(url):
    """
    This method is used for:
        -retrieving message text, when the webhook is triggered with a message
        -Getting the username of the person who posted the message if a command is recognized
    """
    request = urllib2.Request(url,
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

def sendSparkPOST(url, data):
    """
    This method is used for:
        -posting a message to the Spark room to confirm that a command was received and processed
    """
    request = urllib2.Request(url, json.dumps(data),
                            headers={"Accept" : "application/json",
                                     "Content-Type":"application/json"})
    request.add_header("Authorization", "Bearer "+bearer)
    contents = urllib2.urlopen(request).read()
    return contents

@post('/')
def index(request):
    """
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark,
    using the sendSparkGet() function.  The message text is parsed and sent to Giphy; the result URL is then passed back to the Spark room.
    """
    webhook = json.loads(request.body)
    #print webhook['data']['id']
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
    result = json.loads(result)
    print result
    msg = None
    if webhook['data']['personEmail'] != bot_email:
        in_message = result.get('text', '').lower()
        in_message = in_message.replace(bot_name, '')
        in_message = in_message.strip()
        use_message = in_message.replace(" ", "%20")
        print use_message
        giphy_result = giphyGET('http://api.giphy.com/v1/gifs/translate?s={0}&api_key={1}&rating=pg-13'.format(use_message,giphy_API))
        giphy_result = json.loads(giphy_result)
        if len(giphy_result['data']) > 0:
            giphy_url = giphy_result["data"]["images"]["fixed_height"]['url']
            msg = giphy_url
        if msg != None:
            print msg
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "files": msg})
        else:
            msg = "No results found for {0}".format(in_message)
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})
    return "true"

####CHANGE THESE VALUES#####
bot_email = "bot_email"
bot_name = "bot_name"
bearer = "bot_token"

run_itty(server='wsgiref', host='0.0.0.0', port=10015)
