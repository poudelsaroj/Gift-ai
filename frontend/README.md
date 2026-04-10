# Frontend

This is the production operator console frontend built with Next.js. FastAPI remains the backend and serves all ingestion, normalization, and source action APIs.

## Run

1. Install dependencies:
   `npm install`
2. Point the frontend at FastAPI:
   `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`
3. Start the app:
   `npm run dev`

## Notes

- The app expects the FastAPI backend to expose `/api/v1/ui/console-state` and `/api/v1/ui/records`.
- Source actions, scheduler actions, and file imports are executed directly against FastAPI.
