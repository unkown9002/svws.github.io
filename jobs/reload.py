import docker, subprocess, os, stat, sys, traceback

def reload() :

	# Linux or single Docker use case
	if os.path.isfile("/usr/sbin/nginx") and os.path.isfile("/tmp/nginx.pid") :
		proc = subprocess.run(["/usr/sbin/nginx", "-s", "reload"], capture_output=True)
		if proc.returncode != 0 :
			print("[!] Can't reload nginx (status code = " + str(proc.returncode) + ")")
			if len(proc.stdout.decode("ascii")) > 1 :
				print(proc.stdout.decode("ascii"))
			if len(proc.stderr.decode("ascii")) > 1 :
				print(proc.stderr.decode("ascii"))
			return 0
		return 1

	# Autoconf case (Docker, Swarm and Ingress)
	if os.path.exists("/tmp/autoconf.sock") and stat.S_ISSOCK(os.stat("/tmp/autoconf.sock")) :
		client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		client.connect("/tmp/autoconf.sock")
		client.send("reload".encode("utf-8"))
		data = client.recv(512)
		client.close()
		if not data or data.decode("utf-8") != "ok" :
			print("[!] Can't reload nginx (data not ok)")
			return 0
		return 1

	return 2

if __name__ == "__main__" :
	try :
		print("[*] Starting reload operation ...")
		ret = reload()
		if ret == 0 :
			sys.exit(1)
		elif ret == 1 :
			print("[*] Reload operation successfully executed")
		elif ret == 2 :
			print("[*] Skipped reload operation because nginx is not running")
		sys.exit(0)
	except :
		print("[!] Can't reload nginx (exception)")
		print(traceback.format_exc())
		sys.exit(2)