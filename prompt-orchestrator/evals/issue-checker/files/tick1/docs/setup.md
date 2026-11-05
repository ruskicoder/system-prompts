# Local setup

1. `npm ci`
2. Copy `.env.example` to `.env.local`.
3. Set `VITE_MAP_TOKEN` in `.env.local` to the token from the team vault (entry "map tiles dev").
   Without it the tile server answers 401 and the map renders blank, with no other error.
4. `npm run dev`, then open http://localhost:5173.
