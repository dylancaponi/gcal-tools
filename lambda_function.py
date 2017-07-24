import calendar

# from pprint import pprint
import boto3
import tempfile
import uuid
# import urllib

        
def lambda_handler(event, context):
    print '>>> START LAMBDA <<<'
    
    region_name = 'us-west-2'
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key'] 
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

    print 'bucket_name: ' + bucket
    print 'key: ' + key
    print 'download_path: ' + download_path
    
    s3_client = boto3.client('s3')
    s3_client.download_file(bucket, key, download_path)
    
    with open(download_path, 'r') as f:
        parse_message(f)


def parse_message(body):
    next_line = body.readline()
    days_of_week = list(calendar.day_name)
    event_body = ""
    date = None
    while next_line != "":
      # set the date
      if any(day.lower() in next_line.lower() for day in days_of_week):
        date = next_line.strip()

      elif date:
        # start of event, submit old event
        if next_line.startswith("WHAT: "):
          if event_body != "":
            # submit_event(service, calendar_id, event_body)
            print event_body.replace("\n", "")
            print '---'
          append_description = ""
          event_body = next_line
        elif next_line.startswith("WHO: "):
          append_description += next_line
        elif next_line.startswith("WHEN: "):
          event_body += next_line.replace("WHEN: ", "WHEN: " + date)
        elif next_line.startswith("WHERE: "):
          event_body += next_line
        elif next_line.startswith("CONTACT: "):
          event_body += next_line.replace("CONTACT:", "DESCRIPTION:") + append_description
        elif next_line.isspace():
          pass
        elif next_line.startswith("NEW: "):
          pass
          # or add to title?
        elif next_line.startswith("*Random Fact of the Day:") or next_line.startswith("*CONFIDENTIALITY NOTICE:"):
          break
        else:
          event_body += next_line
          # pass


      next_line = body.readline()
    # submit final event
    print 'final event ---'
    print event_body.replace("\n", "")
    # submit_event(service, calendar_id, event_body)


# def submit_event(service, calendar_id, event_body):
#   wait = True
#   while wait:
#     try:
#       created_event = service.events().quickAdd(
#         calendarId=calendar_id,
#         # text="WHAT:  2017 Entertainment Industry Dinner WHO:  honoring Bill Prady WHEN: WEDNESDAY MAY 24 6:30pm WHERE:  Beverly Hilton Hotel;  9876 Wilshire Blvd;  Beverly Hills DESCRIPTION:  person phone-number email@email.com").execute()
#         text=event_body).execute()
#       wait = None
#       print 'submitted'
#     except Exception as e:
#       print 'failed'
#       print(e)
#       wait = True
#       print('waiting 5 seconds')
#       time.sleep(5)

