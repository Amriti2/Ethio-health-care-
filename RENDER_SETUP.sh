#!/bin/bash
# RENDER FIREBASE SETUP - Run this in your terminal (Windows PowerShell or Mac/Linux terminal)
# This will add Firebase environment variables to your Render service in seconds

# 1. Get your Render API key from: https://dashboard.render.com/account/api-tokens
# 2. Copy the command below and paste it into your terminal
# 3. Replace YOUR_API_KEY with your actual Render API token
# 4. Replace YOUR_SERVICE_ID with your service ID (see below to find it)

# TO FIND YOUR SERVICE ID:
# - Go to https://dashboard.render.com
# - Click on "ethio-health-care" service
# - Look at the URL - it will be: https://dashboard.render.com/srv/XXXXX
# - That XXXXX is your SERVICE_ID

# QUICK COPY-PASTE (Mac/Linux/WSL):
curl -X PATCH "https://api.render.com/v1/services/YOUR_SERVICE_ID" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "envVars": [
      {
        "key": "FIREBASE_DATABASE_URL",
        "value": "https://ethiohealthcare-6ad15-default-rtdb.firebaseio.com"
      },
      {
        "key": "FIREBASE_CREDENTIALS",
        "value": "{\"type\":\"service_account\",\"project_id\":\"ethiohealthcare-6ad15\",\"private_key_id\":\"b5a35c1ffad3c4587a84242405dfee16c0c35691\",\"private_key\":\"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCpvuAPiRPEntsj\nMmGDmmYRgWUqgPiLhr0l06+OKwtftFDOGNUJE83SBzFk8sIDK5WtYlfG08n9rAeG\nOHSFrFMhJjfedna4mfAB19/KZqkRNXHainz62+q+NHxmjzUc9Eg1/tNPJoq/sIBz\nEp5FMkpo7ePA+ItBN/nGGb+74dipoGYn18Y7O6sVqqHisjieHriMSz28OSIwlK6w\n0I1FfVJ46jvUvCJhueCW3nxTpPEswroZDEI8VKmLAvyE5N+7/bBn4/wnvNV5GESN\n5vF71ZB/zTCXD6wq1zmxeGdnuEy1dgVNHIbBVNkY993Lqo5bSX1x9n8nRVGEMZGV\ntERl6mznAgMBAAECggEAVIbrVnEhOekNILLG4lzxdMglk4vTuM8ow3xtUHNY35iQ\nIIE3HKUS+gKA8077k86RY1y0bxsp27tdp9XXGHWek8RPT+VX60ckwBY6p7SFfj9J\n6dTKtbTraToDtKKdhUST7OdvXFvJ/firjiH4VGbdrPDBWGesGJcCN0a9NpcZaCXa\n+46U/57wY27ZPvU2IQWVDd15Ix2GjoRWaWwO5QPmJyBzLxBctruQPZS61kqiF73p\nh9yw6Bs+jhq8kis8tqV54uIiz/BGhCGssgb40/zkTt+Q2hjN3oIS9Ld/yKfkv9gg\nZpzKT9UINGsr91q+fXlgXOxAJXMf5Q2THt7TfI4QMQKBgQDRiODKyoSL7MknSIw6\nIKk6h5LUhdybACVknjbzuzmqRh6x4EeDoW4p7IWLaus84CymbP1VeukFHhVrTvuz\nSvOx3C7WkgDN64ZG4rxbFIGxEjuA2MEsVIyfGsNJ+GKaa0s0rbmE21eTMe+OfZLq\npHNsTK2KKsHk3jPMTzRlyQjKnwKBgQDPYzPBehT6qjdkg5WiUTgaE/s2np2HYo2T\nr5HCwvL4Ba92KNv6l4jOMoJ7PGm4bB7VOZ+ThRqq9wZ5vbaqMfAMhYKpvOaM0zv+\nqMrJJiKxvJAEjxwllePM11ddBRfzUkN5waY55O17a71yv95wl0eLYbKAhBfCFmml\nBBb453AAuQKBgGG/dgaEdVMFUk2WJXyUcf3Q8ylbjS9t4QPQXxhStjL95SHb2+DH\nNSovoZkJdtX+SjYVUBVJcl0lzJ4zyW25wHevnNYSZHersQdujKn8pgfh1opkE7HH\ne5ZZmNLwIaeh+AKKLKqS3IbZW8TgReJad1IFb0uuaKeJFSbxqCL3prdHAoGAMKWX\nhWHqu+Xjuns3RW0B2PQo8GYCk7hld2guq93o+o7y2qe4+i5DlAK7IsdIEU+jZ+bt\nbMBDQilR5oq+52txYK6MuN4rwormPtU/RDHi34hYzAj51EM1vV4iCxrfxF7enxfy\nsw/lORdLyDgDqKuDx8kyAv15STjSrTepX9eCKVkCgYEArRiZYNMvXobKhWtIidgo\nfnTGUubISrvB0c85TDkFNHSF3kAvrmGsBGCSx5h80Fw5ZLXtRrn9inMLpW/BczUz\nMLDKLMy/7FoZbHOng8fGiQzEPIRIs0fpM7SxHcyu8rEI9+u2JpJiMy1iG/NOXNf0\nEPtwUE5FzKZ70wAn0kNBVPw=\n-----END PRIVATE KEY-----\n\",\"client_email\":\"firebase-adminsdk-fbsvc@ethiohealthcare-6ad15.iam.gserviceaccount.com\",\"client_id\":\"112707536730799930875\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://oauth2.googleapis.com/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"client_x509_cert_url\":\"https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40ethiohealthcare-6ad15.iam.gserviceaccount.com\",\"universe_domain\":\"googleapis.com\"}"
      }
    ]
  }'

# WINDOWS PowerShell version (if curl doesn't work):
# Invoke-WebRequest -Uri "https://api.render.com/v1/services/YOUR_SERVICE_ID" `
#   -Method PATCH `
#   -Headers @{"Authorization"="Bearer YOUR_API_KEY"; "Content-Type"="application/json"} `
#   -Body (ConvertTo-Json @{envVars=@(@{key="FIREBASE_DATABASE_URL";value="https://ethiohealthcare-6ad15-default-rtdb.firebaseio.com"},@{key="FIREBASE_CREDENTIALS";value="{...}"})})
