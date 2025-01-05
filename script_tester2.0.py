import http.client

conn = http.client.HTTPSConnection("whin2.p.rapidapi.com")

headers = {
   

conn.request("GET", "/mygroup", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
