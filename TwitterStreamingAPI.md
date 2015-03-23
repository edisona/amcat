https://dev.twitter.com/docs/streaming-api/methods

Example tracking search terms:
```
$ echo "track=politiek,denhaag,nieuws" > tracking
$ curl -d @tracking https://stream.twitter.com/1/statuses/filter.json -ufloorter:password
```

Output: 1 tweet per regel in json

```
{
    "truncated":false,
    "text":"@geertwilderspvv wat mij betreft heiloze missie en zonde van het geld. Korte termijn politiek",
    "id_str":"136052990887985153",
    "retweeted":false,
    "in_reply_to_status_id_str":"136047524321562625",
    "in_reply_to_user_id":41778159,
    "in_reply_to_user_id_str":"41778159",
    "entities":{
        "urls":[],
        "user_mentions":[{
            "indices":[0,16],
            "id_str":"41778159",
            "screen_name":"geertwilderspvv",
            "name":"Geert Wilders",
            "id":41778159
        }],
        "hashtags":[]
    },
    "source":"\u003Ca href=\"http:\/\/twitter.com\/download\/android\" rel=\"nofollow\"\u003ETwitter for Android\u003C\/a\u003E",
    "created_at":"Mon Nov 14 12:08:55 +0000 2011",
    "contributors":null,
    "place":null,
    "geo":null,
    "favorited":false,
    "coordinates":null,
    "user":{
        "contributors_enabled":false,
        "notifications":null,
        "profile_use_background_image":true,
        "id_str":"220698808",
        "profile_text_color":"333333",
        "default_profile":true,
        "show_all_inline_media":true,
        "profile_background_image_url":"http:\/\/a0.twimg.com\/images\/themes\/theme1\/bg.png",
        "favourites_count":18,
        "profile_link_color":"0084B4",
        "description":"Jeugdbeschermer",
        "lang":"en",
        "time_zone":"Amsterdam",
        "created_at":"Sun Nov 28 15:46:09 +0000 2010",
        "is_translator":false,
        "follow_request_sent":null,
        "profile_background_image_url_https":"https:\/\/si0.twimg.com\/images\/themes\/theme1\/bg.png",
        "friends_count":40,
        "profile_background_color":"C0DEED",
        "followers_count":44,
        "profile_image_url":"http:\/\/a0.twimg.com\/profile_images\/1177821343\/IMG_7851_normal.JPG",
        "listed_count":1,
        "geo_enabled":false,
        "profile_background_tile":false,
        "screen_name":"yvonne1808",
        "following":null,
        "verified":false,
        "profile_sidebar_fill_color":"DDEEF6",
        "protected":false,
        "url":null,"statuses_count":1714,
        "name":"yvonne",
        "profile_sidebar_border_color":"C0DEED",
        "id":220698808,
        "default_profile_image":false,
        "utc_offset":3600,
        "profile_image_url_https":"https:\/\/si0.twimg.com\/profile_images\/1177821343\/IMG_7851_normal.JPG",
        "location":"Noord-Holland"
    },
    "in_reply_to_status_id":136047524321562625,
    "id":136052990887985153,
    "retweet_count":0,
    "in_reply_to_screen_name":"geertwilderspvv"
}
```