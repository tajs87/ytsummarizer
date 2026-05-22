# User Guide

## Getting Started

1. Open the frontend at `http://localhost:5173`
2. Login or register an account
3. Submit a supported video URL

## Supported Video URLs

- YouTube links
- Vimeo links
- Direct video file URLs (`.mp4`, `.mov`, `.webm`, etc.)

## Basic Transcription Workflow

1. Paste video URL in the input box
2. Click **Start Transcription**
3. Wait for processing status updates
4. Open video details to view transcription
5. Search transcription or export as TXT/CSV/JSON

## Summary Generation

1. Open a video that has completed transcription
2. Trigger summary generation
3. Choose summary type:
   - Brief
   - Detailed
   - Bullet points
4. View generated summary and highlights

## Sharing Timestamp Links

1. Open video detail or summary highlights
2. Click **Share** near a timestamp
3. Optionally set title and expiration
4. Copy generated link
5. Share the link publicly

## History Page

Use **View History** to:
- See all previous videos
- Filter by processing status
- Open completed videos
- Delete entries

## Troubleshooting

### Video fails to process
- Verify URL is valid and publicly accessible
- Confirm platform is supported
- Check backend and worker logs

### Transcription fails
- Ensure OpenAI API key is set in environment
- Ensure OpenAI account has available credits

### Summary fails
- Verify transcription completed successfully first
- Check OpenAI API quota and model access
