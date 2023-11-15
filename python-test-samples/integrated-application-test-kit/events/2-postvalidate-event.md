# PostValidate Event Payload

Here is the event documentation of the event you will get listening for the `postValidate` hook.

The `detail` object of the event you receive will contain information you may be interested in.

### Example `detail` payload

```json
    //...


    { 
        "detail": {
            "video": {
            "author": {
              "username": "soldier369"
            },
            "createdAt": "2023-10-12T10:14:44.167Z",
            "durationmillis": 144000,
            "thumbnail": "https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/thumbnails/thumb0.jpg",
            "playbackUrl": "https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/hls/720p30/output.mp4",
            "channel": "78918340-d081-7059-632f-62ce34e1d4ed",
            "recording_s3_key_prefix": "ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3",
            "id": "st-1EQqxfA8cn37wyFj9QsBFqn",
            "streamUrl": "https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/hls/master.m3u8"
          },
            "pluginData": {
                "preValidate": [
                    {
                    "OutputKey": "plugin-content_moderation_plugin",
                    "OutputValue": {
                        "valid": true,
                        "reason": "No offensive content found in video"
                    }
                    },
                    {
                    "OutputKey": "plugin-duration_plugin",
                    "OutputValue": {
                        "valid": true
                    }
                    }
                ],    
            },
            "taskToken": "..."
        }
    }
  //...
```

**Details of each property**

| Property                      | type     | Description                                                                                         |
| ----------------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| video                         | `Video`  | The video domain object that has been created                                                       |
| video.createdAt               | `string` | The time the video was created                                                                      |
| video.durationmillis          | `number` | The duration of the video (in milliseconds)                                                         |
| video.playbackURL             | `string` | The URL video itself in `mp4` format.                                                               |
| video.streamURL               | `string` | The URL of the video master playlist in `m3u8` format.                                              |
| video.channel                 | `string` | The id of the channel the video belongs too, each user has a channel, channels can have many videos |
| video.id                      | `string` | The id of the video                                                                                 |
| pluginData                    | `object` | Object the stores the plugin information.                                                           |
| pluginData.{hook}             | `array`  | Array of objects that store the output of any plugins that occured before it                        |
| pluginData.{hook}.OutputKey   | `string` | A plugin id that the data belongs too                                                               |
| pluginData.{hook}.OutputValue | `string` | The output of the plugin                                                                            |
| taskToken                     | `string` | The step functions task token you need to use to continue the plugin manager.                       |
| author.username               | `string` | The author/broadcaster of the video                                                                 |


### Raise test events directly into your plugin

You can use the AWS CLI to rasie events directly into your plugin, here is an example:

Replace the `detailType` with your plugin name.

```sh
aws events put-events --entries '[{"Source": "ServerlessVideo.pluginManager", "DetailType": "postValidate.generateTitlePlugin", "Detail": ""{\"video\":{\"author\":{\"username\":\"soldier369\"},\"createdAt\":\"2023-10-05T13:53:52.825Z\",\"durationmillis\":144000,\"thumbnail\":\"https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/thumbnails/thumb0.jpg\",\"playbackUrl\":\"https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/hls/720p30/output.mp4\",\"channel\":\"78918340-d081-7059-632f-62ce34e1d4ed\",\"id\":\"st-1EQqxfA8cn37wyFj9QsBFqn\"},\"taskToken\":\"AQCgAAAAKgAAAAMAAAAAAAAAARnUhXm6/7iN2pgIQDiBVCl0X8ayClanna2bwMlMfQ2gRMT29xDKrtchtadLT8Ke21erbmXyKjdYDZ0F5IsfhdQQN7mUV3IpS
"}]'
```

