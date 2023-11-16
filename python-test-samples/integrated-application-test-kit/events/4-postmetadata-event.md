# Postmetadata Event Payload

Here is the event documentation of the event you will get listening for the `postMetadata` hook.

The `detail` object of the event you receive will contain information you may be interested in.

### Example `detail` payload

```json
    //...
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
            "postValidate": [],
            "preMetadata": [
              {
                "OutputKey": "plugin-transcribeplugin",
                "OutputValue": {
                  "TranscriptFilePointers": {
                    "TranscriptFileUri": "https://s3.us-west-2.amazonaws.com/serverlessvideo-basecore-cdnstack-p6b-originbucket-qf6cyql0kb4m/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/transcribe.json",
                    "SubtitleFileUris": [
                      "https://s3.us-west-2.amazonaws.com/serverlessvideo-basecore-cdnstack-p6b-originbucket-qf6cyql0kb4m/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/transcribe.vtt"
                    ]
                  }
                }
              }
            ]
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
| video.channel                 | `string` | The id of the channel the video belongs too, each user has a channel, channels can have many videos |
| video.id                      | `string` | The id of the video                                                                                 |
| pluginData                    | `object` | Object the stores the plugin information.                                                           |
| pluginData.{hook}             | `array`  | Array of objects that store the output of any plugins that occured before it                        |
| pluginData.{hook}.OutputKey   | `string` | A plugin id that the data belongs too                                                               |
| pluginData.{hook}.OutputValue | `string` | The output of the plugin                                                                            |
| taskToken                     | `string` | The step functions task token you need to use to continue the plugin manager.                       |
| author.username               | `string` | The author/broadcaster of the video                                                                 |

## Example Full Payload

```json
{
    "version": "0",
    "id": "054235b8-3936-ad39-e821-8bcf2b3e9366",
    "detail-type": "postMetadata.generateTitlePlugin",
    "source": "ServerlessVideo.pluginManager",
    "account": "832196373597",
    "time": "2023-08-31T10:03:25Z",
    "region": "us-west-2",
    "resources": [
        "arn:aws:states:us-west-2:832196373597:stateMachine:832196373597-us-west-2-PluginLifecycleWorkflow",
        "arn:aws:states:us-west-2:832196373597:execution:832196373597-us-west-2-PluginLifecycleWorkflow:9c56bea3-f552-4771-bc0a-509b1af68618"
    ],
    "detail": {
        "video": {
            "createdAt": "2023-08-30T14:57:51.169Z",
            "durationmillis": 24000,
            "thumbnail": "https://dmpdx8pmqxo3f.cloudfront.net/media/ivs/v1/832196373597/ERaAhUZnrHJG/2023/8/30/14/57/ovoTjGdG38Mk/media/hls/720p30/thumbnails/thumb0.jpg",
            "playbackUrl": "https://dmpdx8pmqxo3f.cloudfront.net/media/ivs/v1/832196373597/ERaAhUZnrHJG/2023/8/30/14/57/ovoTjGdG38Mk/media/hls/720p30/output.mp4",
            "channel": "08d143f0-00f1-7052-f97a-cbcda39ff077",
            "id": "st-1E4rsUkhLinpvScDxzDQ7ql",
            "author": {
                "username": "random1"
            }
        },
        "pluginData": {
            "preValidate": [
                {
                    "OutputKey": "plugin-duration_plugin",
                    "OutputValue": {
                        "valid": true
                    }
                }
            ],
            "postValidate": [
                {
                    "Entries": [
                        {
                            "EventId": "b784478f-a460-6f1a-af50-5cc42e895b80"
                        }
                    ],
                    "FailedEntryCount": 0
                }
            ],
            "preMetadata": [
                {
                    "OutputKey": "plugin-transcribeplugin",
                    "OutputValue": {
                        "transcript": "Uh, is this working? I don't really know. It autos to the forward facing camera works. All right. I'll stop now."
                    }
                }
            ]
        },
        "taskToken": "AQCgAAAAKgAAAAMAAAAAAAAAAZiPlrHGCTsL4I66zysrOw4pXGoGeECfKjSmHgAVLj9uQ5hocHhVxPHbOCjQS3xIa7QEsP27+MiU2a5fxp+Uwo0ft6YbgJhddLR7KRbB+LlyvRe098LSOREVUdhbO4AEWDwaMc4r8w==OlhIwTvLrVhnfr1A2UCyUinqpK0WQn/FnROd+7Q3viKLGB3RpdkCjT/j1jw71aU5GkQoapmi4O+dJZN5LCbkZMcJ5LIQ6PsYQvLkQ55Vuzv4UnwSRHzt9BcpGzqv+q1PgYdAJIVKJsb82a9KwBIzE4620bhSrpdQL/2Zq++AoCgjBGSkT2lDyZ99iqErDTtGk0wkBtZvWrONhmVxXU3QmA7ouVm4dgjTVl4qQHWZG9U33uUuQHw/t1KfIp4WL0ds+hJ/hPDefFwH791qj6fo0MXm0apOA2JXcURD84j8/0QOkPx3zbGVBuYr8AzMeCE++5e9FjcJu1w913FSpvnDkLf92C8Cp1QvcPJ1SnQKTokz1YE8oqwlHM2zo1Mzu6tX5nAUN5m8hHfndhcA6u6sUSSqAzhtICN64t9KPl9AmNy4CdZE6+lGMZuqxeL2xCHVXySb7nsnnpe/KujCkoQhVbdvGJcZJ01q+SWUXCVyS+0mopueDiwjMR6S/QqjoIjgQNP5NtA7ee2/u5XVQnNj"
    }
}
```

### Raise test events directly into your plugin

You can use the AWS CLI to raise events directly into your plugin, here is an example:

Replace the `detailType` with your plugin name.

```sh
aws events put-events --entries '[{"Source": "ServerlessVideo.pluginManager", "DetailType": "postMetadata.generateTitlePlugin", "Detail": "{\"video\":{\"createdAt\":\"2023-08-30T14:57:51.169Z\",\"durationmillis\":24000,\"thumbnail\":\"https://dmpdx8pmqxo3f.cloudfront.net/media/ivs/v1/832196373597/ERaAhUZnrHJG/2023/8/30/14/57/ovoTjGdG38Mk/media/hls/720p30/thumbnails/thumb0.jpg\",\"playbackUrl\":\"https://dmpdx8pmqxo3f.cloudfront.net/media/ivs/v1/832196373597/ERaAhUZnrHJG/2023/8/30/14/57/ovoTjGdG38Mk/media/hls/720p30/output.mp4\",\"channel\":\"08d143f0-00f1-7052-f97a-cbcda39ff077\",\"id\":\"st-1E4rsUkhLinpvScDxzDQ7ql\"},\"pluginData\":{\"preValidate\":[{\"OutputKey\":\"plugin-duration_plugin\",\"OutputValue\":{\"valid\":true}}],\"postValidate\":[{\"Entries\":[{\"EventId\":\"b784478f-a460-6f1a-af50-5cc42e895b80\"}],\"FailedEntryCount\":0}],\"preMetadata\":[{\"OutputKey\":\"plugin-transcribeplugin\",\"OutputValue\":{\"transcript\":\"Uh, is this working? I dont really know. It autos to the forward facing camera works. All right. I will stop now.\"}}]},\"taskToken\":\"AQCgAAAAKgAAAAMAAAAAAAAAAZiPlrHGCTsL4I66zysrOw4pXGoGeECfKjSmHgAVLj9uQ5hocHhVxPHbOCjQS3xIa7QEsP27+MiU2a5fxp+Uwo0ft6YbgJhddLR7KRbB+LlyvRe098LSOREVUdhbO4AEWDwaMc4r8w==OlhIwTvLrVhnfr1A2UCyUinqpK0WQn/FnROd+7Q3viKLGB3RpdkCjT/j1jw71aU5GkQoapmi4O+dJZN5LCbkZMcJ5LIQ6PsYQvLkQ55Vuzv4UnwSRHzt9BcpGzqv+q1PgYdAJIVKJsb82a9KwBIzE4620bhSrpdQL/2Zq++AoCgjBGSkT2lDyZ99iqErDTtGk0wkBtZvWrONhmVxXU3QmA7ouVm4dgjTVl4qQHWZG9U33uUuQHw/t1KfIp4WL0ds+hJ/hPDefFwH791qj6fo0MXm0apOA2JXcURD84j8/0QOkPx3zbGVBuYr8AzMeCE++5e9FjcJu1w913FSpvnDkLf92C8Cp1QvcPJ1SnQKTokz1YE8oqwlHM2zo1Mzu6tX5nAUN5m8hHfndhcA6u6sUSSqAzhtICN64t9KPl9AmNy4CdZE6+lGMZuqxeL2xCHVXySb7nsnnpe/KujCkoQhVbdvGJcZJ01q+SWUXCVyS+0mopueDiwjMR6S/QqjoIjgQNP5NtA7ee2/u5XVQnNj\"}"}]'
```
