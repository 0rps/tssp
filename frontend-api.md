# Authorization

###### `POST /api/auth/`

**Response:**
* HTTP code 302 - success
* HTTP code 4xx -> validation error


# Configuration

### Set game configuration

##### `POST /api/config/`

**Request:**
```json
{
	// int: 1 or 2
	"auction_type": 1,
	// "free" or "script"
	"mode": "free",
	// int
	"impressions_total": 0,
	// int
	"budget": 0,
	// int
	"impression_revenue": 0,
	// int
	"click_revenue": 0,
	// int
	"conversion_revenue": 0,
	// int
	"frequency_capping": 0,
	// "revenue" or "cpc"
	"game_goal": "revenue",
	// bool
	"frequency_capping_enabled": false,
	// bool
	"ads_txt_enabled": false
}
```
**Response**
Should return 200. Otherwise show modal window (or just call `alert(error_text)`) with HTTP code and content.


##### `GET /api/config/`

**Response:**

* HTTP code 200
* Content:
```json
{
	// int: 1 or 2
	"auction_type": 1,
	// "free" or "script"
	"mode": "free",
	// int
	"impressions_total": 0,
	// int
	"budget": 0,
	// int
	"impression_revenue": 0,
	// int
	"click_revenue": 0,
	// int
	"conversion_revenue": 0,
	// int
	"frequency_capping": 0,
	// "revenue" or "cpc"
	"game_goal": "revenue",
	// bool
	"frequency_capping_enabled": false,
	// bool
	"ads_txt_enabled": false
}
```

### Teams

##### `POST /api/teams/`

**Request:**
```json
{
	// string
	"name": "team name",
	// string
	"api_url": "http://127.0.0.1:8080",
	// string or empty string
	"bearer_token": "some_bearer_token"
}
```

**Response:**
* HTTP code 201
* Content
```json
{
	//int
	"id": 5,
	// string
	"name": "team name",
}
```

##### `DELETE /api/teams/<id>/`

**Response:**
* HTTP Code 204


##### `GET /api/teams/`

**Response:**

* HTTP Code 200
* Content:
```json 
[
	{
		//int
		"id": 5,
		// string
		"name": "team name a",
	},
	{
		//int
		"id": 6,
		// string
		"name": "team name b",
	},
]

```

# Game
##### `POST /api/game/adrequest/`

**Request:**
* Empty

**Response:**
* HTTP Code: 200
* Content:  
```json
{
	//int
	"round": 12,
	// bool, if has_next_round is false => show button with "Scoreboard" (it is the end of the game)
	"has_next_round": false,
	"bidrequest": {
		// string
		"id": "bidrequest_id",  
		"imp": {
			"banner": {
				// int
		 		"w": 240,
		 		// int
		  		"h": 120
			},
		},
		"click": { 
			//float
			"prob": 0.9
		},
		"conv": { 
			// float
			"prob": 0.75
		},
		"site": {
			// string
			"domain": "www.nytimes.com"
		},
		"ssp": {
			//string
	  		"id": "TEST_SSP" 
		},
		"user": {
			// string
			"id": "test_user_ssp101"
		},
		// list of strings, aka blocked categories
		"bcat": ["IAB1", "IAB2", "IAB3"],
	},
	// bidresponse may be null or empty because of nobid. Show "No bid" text in this case 
	"bidresponse": {
		// float
		"price": 7.98,
		// string
		"external_id": "asdfsad",
		// URL as string
		"image_url": "https://shutterstock/1/",
		// list of strings
		"cat": ["IAB1", "IAB2"],
		// string
		"team": "team_name",
		// bool
		"click": true,
		// bool
		"conversion": false,  
		// float
		"final_pctr": 0.65,
		// float
		"final_pcvr": 0.25,
		// float
		"final_price": 5.2,
		"image_size": {
			// int
			"w": 100,
			// int 
			"h": 150
		},
	},
	"teams": [ 
		{
			// string
			"name": "team name",
			// float
			"budget": 12.1,
			// float
			"score": 4.5,
			// int
			"impressions": 4,
			// int
			"clicks": 2,
			// int
			"conversions": 0
		}
	],
	"logs": [
		{
			"team_name": "",
			"message": "", 
		},
		{
			"team_name": "",
			"message": "", 
		},
	]
}
```

Should return 200. Otherwise please add modal window (or just call `alert(error_text)`) with HTTP code and response content.


##### `GET /api/game/state/`

**Response:**
* HTTP Code 200
* Content:
```json

{
	// "new_game", "in_progress", "finished", 
	// "new_game" -> show "Start game" button
	// "in progress" -> show "Next" button and show teams in right side bar
	// "finished" -> show scoreboard with the values from "team" parameter below
	"state": "in_progress",
	"round": 10,
	"teams": [
		{
			// string
			"name": "",
			// float
			"budget": 12.2,
			// float
			"score": 4.5,
			// int
			"impressions": 4,
			// int
			"clicks": 2,
			// int
			"conversions": 0
		}
	]
}

```


##### `POST /api/game/reset/`

Resets state of the game and team states

**Response:**
* HTTP Code 200
```
