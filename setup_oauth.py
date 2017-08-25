import praw
r = praw.Reddit(client_id='XXX',
                client_secret='XXX',
                redirect_uri='http://localhost:8080',
                user_agent='Baseball Game Thread for Reddit - Setup v1.0 https://github.com/toddrob99/Baseball-GDT-Bot')

url = r.auth.url(['identity', 'submit', 'edit', 'read', 'modposts', 'privatemessages', 'flair', 'modflair'], '...', 'permanent')
import webbrowser
webbrowser.open(url)

var_input = raw_input("Enter code: ")
access_information = r.auth.authorize(var_input)
print "Refresh token:",access_information
raw_input()
