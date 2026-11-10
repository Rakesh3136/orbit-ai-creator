# AIMN to ORBIT local production handoff

AIMN now accepts a structured script on an internal `producer` task and hands it to the existing ORBIT production renderer. This is a local render only: no web assets are downloaded, no YouTube upload is performed, and no external action is dispatched.

## Create a producer task

Create an internal task (`external_action: false`) using the authenticated task API. Supply `input_payload`:

```json
{
  "agent_id": "producer",
  "title": "Render the approved episode",
  "instruction": "Render this owner-supplied script locally.",
  "external_action": false,
  "input_payload": {
    "narration_backend": "auto",
    "script": {
      "title": "Why the Internet Has a Physical Cost",
      "hook": "The internet feels invisible, but every tap depends on real machines.",
      "body": "Data centers store and process information.\\n\\nNetworks move that information between people and services.",
      "conclusion": "The digital world is built on physical infrastructure."
    }
  }
}
```

The script fields are required. The request payload is limited to 32 KB; title, hook, body and conclusion have individual limits. Renders are capped at 12 scenes and four minutes. Narration backend can be `auto`, `espeak` or `silent`.

## Outputs

The dashboard now shows the Producer script fields when you select the Producer agent. When rendering completes, the task row provides links to the video, captions and provenance. These links use an authenticated API route that only serves known files inside that completed task directory.

The worker stores files beneath `data/production/<network-id>/<task-id>`:

- `episode.mp4` — locally rendered scene-card video with narration where the local speech engine is available
- `episode.srt` — captions
- `asset_provenance.json` — hashes and origin/licensing notes for generated media
- `package/` — script, render plan and private-by-default publishing package manifest

The Docker worker has FFmpeg, eSpeak NG and DejaVu fonts installed and mounts `./data` persistently. These are free local tools; rendering uses the host's CPU and disk. The asset backup utility includes this output directory.

A producer task without a `script` payload still returns a production brief and does not render. External-action tasks remain excluded from worker dispatch, and this handoff never uploads or publishes to YouTube.
