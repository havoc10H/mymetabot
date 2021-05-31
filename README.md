# Metabot
Simple python application that fetches app metadata from appstore and google playstore

## How it works
`sf-content-insight-bot` runs as a Cloud Function on GCP  

All responses will have the form
```json
{
	"platform": "itunes/android",
	"identifier": "appId for the respective store",
	"data": [
		{
			"source": "url of the app in the store",
			"name": "name of the app in the store",
			"publisher": "developer of the app",
			"category": "genre of the app in the store",
			"raw": "raw response data from the store",
		},
	]
}
```