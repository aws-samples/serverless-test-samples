# Premetadata Event Payload

Here is the event documentation of the event you will get listening for the `preMetadata` hook.

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
            "postValidate": []
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
    "id": "c2996c57-e91e-8e7b-54e4-147d2cc497de",
    "detail-type": "preMetadata.transcribeplugin",
    "source": "ServerlessVideo.pluginManager",
    "account": "832196373597",
    "time": "2023-08-31T10:03:03Z",
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
            ]
        },
        "taskToken": "AQCgAAAAKgAAAAMAAAAAAAAAAWt75fCKm1gDK7Iv4BMxeI3WJTMFRNiJ1gpcLcY7KeHwI3hB/Dy9JnfQyL5Bfm3wzCCfcTZD8czzxyeY7VYb97xtycdxKsBsiwwOQ0cJ41FfDjdNPmI5Yn9OK1rdlyf64Bd1ZnhJNQ==1qSa17DZLyI2IbOd+NBjooFp1k64s84dF+Xw+3mUJD/yuZ4fPXm55AQjS8vSKZi+9Pf+HY/nBQXuImvSM4cxBTYBjiHygSAKqGHYxEKNRwhZvjEyFh9Je79dDlpPM6ItQy83rFGqTaJVGZWMPHV/ijE/yg56Sfw4L56NAFzJfRHDYhNhbb31jumnGxdxhP6VPfcYoCsh8Nikz7dvRvWGfmfCp57tr3yx9QEdoBPjTNwkjhYlocml6y5jPI+xwgV8h0uGibp4ulUx+itide3W2DiqJkNanmf0sOv9Im7TQv3YIB7RCE3xJKGWsCavMEk59N5P9Pl7moYseCShsgowjCVRaCQrKFaf4GyxYa5jvfmAXqmcCbJqE95+fS9FUGn1E/sr/oy1I5RVb3ZqkbQPoUJBXkSgygvwMnmRTcN9miBQl3pV7CGI3OO2uECpNbLXgcXhB62UE54EPsOVA+YZrKarn2Wn3x5pDN1T9+jxwDProFDcN12sIhxIMba0b5CzeX6GOj2doo1sb9+oFuyy"
    }
}
```
### Raise test events directly into your plugin

You can use the AWS CLI to rasie events directly into your plugin, here is an example:

Replace the `detailType` with your plugin name.

```sh
aws events put-events --entries '[{"Source": "ServerlessVideo.pluginManager", "DetailType": "preMetadata.generateTitlePlugin", "Detail": "{\"video\":{\"createdAt\":\"2023-08-30T14:57:51.169Z\",\"durationmillis\":24000,\"thumbnail\":\"https://dmpdx8pmqxo3f.cloudfront.net/media/ivs/v1/832196373597/ERaAhUZnrHJG/2023/8/30/14/57/ovoTjGdG38Mk/media/hls/720p30/thumbnails/thumb0.jpg\",\"playbackUrl\":\"https://dmpdx8pmqxo3f.cloudfront.net/media/ivs/v1/832196373597/ERaAhUZnrHJG/2023/8/30/14/57/ovoTjGdG38Mk/media/hls/720p30/output.mp4\",\"channel\":\"08d143f0-00f1-7052-f97a-cbcda39ff077\",\"id\":\"st-1E4rsUkhLinpvScDxzDQ7ql\"},\"pluginData\":{\"preValidate\":[{\"OutputKey\":\"plugin-duration_plugin\",\"OutputValue\":{\"valid\":true}}],\"postValidate\":[{\"Entries\":[{\"EventId\":\"b784478f-a460-6f1a-af50-5cc42e895b80\"}],\"FailedEntryCount\":0}]},\"taskToken\":\"AQCgAAAAKgAAAAMAAAAAAAAAAWt75fCKm1gDK7Iv4BMxeI3WJTMFRNiJ1gpcLcY7KeHwI3hB/Dy9JnfQyL5Bfm3wzCCfcTZD8czzxyeY7VYb97xtycdxKsBsiwwOQ0cJ41FfDjdNPmI5Yn9OK1rdlyf64Bd1ZnhJNQ==1qSa17DZLyI2IbOd+NBjooFp1k64s84dF+Xw+3mUJD/yuZ4fPXm55AQjS8vSKZi+9Pf+HY/nBQXuImvSM4cxBTYBjiHygSAKqGHYxEKNRwhZvjEyFh9Je79dDlpPM6ItQy83rFGqTaJVGZWMPHV/ijE/yg56Sfw4L56NAFzJfRHDYhNhbb31jumnGxdxhP6VPfcYoCsh8Nikz7dvRvWGfmfCp57tr3yx9QEdoBPjTNwkjhYlocml6y5jPI+xwgV8h0uGibp4ulUx+itide3W2DiqJkNanmf0sOv9Im7TQv3YIB7RCE3xJKGWsCavMEk59N5P9Pl7moYseCShsgowjCVRaCQrKFaf4GyxYa5jvfmAXqmcCbJqE95+fS9FUGn1E/sr/oy1I5RVb3ZqkbQPoUJBXkSgygvwMnmRTcN9miBQl3pV7CGI3OO2uECpNbLXgcXhB62UE54EPsOVA+YZrKarn2Wn3x5pDN1T9+jxwDProFDcN12sIhxIMba0b5CzeX6GOj2doo1sb9+oFuyy\"}"}]'
```
