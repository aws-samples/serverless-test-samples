# Prevalidate Event Payload

Here is the event documentation of the event you will get listening for the `preValidate` hook.

The `detail` object of the event you receive will contain information you may be interested in.

### Example `detail` payload

```json
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
        "taskToken": "..."
      }
    }
```




**Details of each property**

| Property             | type     | Description                                                                                         |
| -------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| video                | `Video`  | The video domain object that has been created                                                       |
| video.createdAt      | `string` | The time the video was created                                                                      |
| video.durationmillis | `number` | The duration of the video (in milliseconds)                                                         |
| video.playbackURL    | `string` | The URL video itself in `mp4` format.                                                               |
| video.streamURL      | `string` | The URL of the video master playlist in `m3u8` format.                                              |
| video.channel        | `string` | The id of the channel the video belongs too, each user has a channel, channels can have many videos |
| video.id             | `string` | The id of the video                                                                                 |
| taskToken            | `string` | The step functions task token you need to use to continue the plugin manager.                       |
| author.username      | `string` | The author/broadcaster of the video                                                                 |


## Example Full Payload

```json
{
  "version": "0",
  "id": "84036a02-7475-25ed-1d57-e7426e3dc553",
  "detail-type": "preValidate.duration_plugin",
  "source": "ServerlessVideo.pluginManager",
  "account": "832196373597",
  "time": "2023-08-31T09:54:38Z",
  "region": "us-west-2",
  "resources": [
    "arn:aws:states:us-west-2:832196373597:stateMachine:832196373597-us-west-2-PluginLifecycleWorkflow",
    "arn:aws:states:us-west-2:832196373597:execution:832196373597-us-west-2-PluginLifecycleWorkflow:59c3b33d-7248-43b3-81e3-5c6205c2a955"
  ],
  "detail": {
        "video": {
          "author": {
            "username": "soldier369"
          },
          "createdAt": "2023-10-05T13:53:52.825Z",
          "durationmillis": 144000,
          "thumbnail": "https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/thumbnails/thumb0.jpg",
          "playbackUrl": "https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/hls/720p30/output.mp4",
          "streamUrl": "https://d3ih6h9pkrghoj.cloudfront.net/ivs/v1/093675026797/nIET8AxYI7Nq/2023/10/5/13/51/8HHcMJ1FCBR3/media/hls/master.m3u8",
          "channel": "78918340-d081-7059-632f-62ce34e1d4ed",
          "id": "st-1EQqxfA8cn37wyFj9QsBFqn"
        },
        "taskToken": "..."
      }
  }

```

### Raise test events directly into your plugin

You can use the AWS CLI to rasie events directly into your plugin, here is an example:

Replace the `detailType` with your plugin name.

```sh
aws events put-events --entries file://events/put-events/prevalidate.json
```


