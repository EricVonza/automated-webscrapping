from twilio.rest import Client

account_sid = 'ACd8936a014ab4a62d75ed47303cabbbb1'
auth_token = '6db12d4925b2f5b08616e8e9e4f2900f'
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
  content_variables='{"1":"12/1","2":"3pm"}',
  to='whatsapp:+254732908889'
)

print(message.sid)