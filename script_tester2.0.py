import http.client

conn = http.client.HTTPSConnection("whin2.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "45b5318b2dmshdf9d3bbbac0730ep1cf77cjsn6e900645baa4",
    'x-rapidapi-host': "whin2.p.rapidapi.com"
}

conn.request("GET", "/mygroup", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))